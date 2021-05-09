import statistics

if __name__ == '__main__':
    import os
    import sys
    import re
    from datetime import datetime
    import pandas as pd
    import pyarrow.parquet as pq
    import time
    import timeit
    import importlib
    import logging

    logging.basicConfig(filename='part_c_tests.log', level=logging.DEBUG,
                        filemode='w', format='%(levelname)s %(asctime)s: %(message)s')
    import metrics

    def test_file_exists(fn):
        if os.path.exists(fn):
            return True
        logging.error(f'{fn} does not exist.')
        return False


    tid_ptrn = re.compile('\d+')


    def invalid_tweet_id(tid):
        if not isinstance(tid, str):
            tid = str(tid)
        if tid_ptrn.fullmatch(tid) is None:
            return True
        return False


    bench_data_path = os.path.join('data', 'benchmark_data_train.snappy.parquet')
    bench_lbls_path = os.path.join('data', 'benchmark_lbls_train.csv')
    queries_path = os.path.join('data', 'queries_train.tsv')
    model_dir = os.path.join('.', 'model')

    start = datetime.now()
    try:
        # is the report there?
        test_file_exists('report_part_c.docx')
        # is benchmark data under 'data' folder?
        bench_lbls = None
        if not test_file_exists(bench_data_path) or \
                not test_file_exists(bench_lbls_path):
            logging.error("Benchmark data does exist under the 'data' folder.")
            sys.exit(-1)
        else:
            bench_lbls = pd.read_csv(bench_lbls_path,
                                     dtype={'query': int, 'tweet': str, 'y_true': int})
            logging.info("Successfully loaded benchmark labels data.")

        # is queries file under data?
        queries = None
        if not test_file_exists(queries_path):
            logging.error("Queries data not found ~> skipping some tests.")
        else:
            queries = pd.read_csv(os.path.join('data', 'queries_train.tsv'), sep='\t')
            logging.info("Successfully loaded queries data.")

        import configuration
        config = configuration.ConfigClass()
        
        # do we need to download a pretrained model?
        model_url = config.get_model_url()
        if model_url is not None and config.get_download_model():
            import utils
            dest_path = 'model.zip'
            utils.download_file_from_google_drive(model_url, dest_path)
            if not os.path.exists(model_dir):
                os.mkdir(model_dir)
            if os.path.exists(dest_path):
                utils.unzip_file(dest_path, model_dir)
                logging.info(f'Successfully downloaded and extracted pretrained model into {model_dir}.')
            else:
                logging.error('model.zip file does not exists.')

        # test for each search engine module
        engine_modules = ['search_engine_' + name for name in ['1']]  # ['1', '2', 'best'] need to change back
        for engine_module in engine_modules:
            try:
                # does the module file exist?
                if not test_file_exists(engine_module + '.py'):
                    continue
                # try importing the module
                se = importlib.import_module(engine_module)
                logging.info(f"Successfully imported module {engine_module}.")
                engine = se.SearchEngine(config=config)
                # test building an index and doing so in <1 minute
                build_idx_time = timeit.timeit(
                    "engine.build_index_from_parquet(bench_data_path)",
                    globals=globals(), number=1
                )
                logging.debug(f"Building the index in {engine_module} for benchmark data took {build_idx_time} seconds.")
                if build_idx_time > 60:
                    logging.error('Parsing and index our *small* benchmark dataset took over a minute!')
                # test loading precomputed model
                engine.load_precomputed_model(model_dir)

                # test that we can run one query and get results in the format we expect
                n_res, res = engine.search('bioweapon')
                if n_res is None or res is None or n_res < 1 or len(res) < 1:
                    logging.error('basic query for the word bioweapon returned no results')
                else:
                    logging.debug(f"{engine_module} successfully returned {n_res} results for the query 'bioweapon'.")
                    invalid_tweet_ids = [doc_id for doc_id in res if invalid_tweet_id(doc_id)]
                    if len(invalid_tweet_ids) > 0:
                        logging.error("the query 'bioweapon' returned results that are not valid tweet ids: " + str(
                            invalid_tweet_ids[:10]))

                # run multiple queries and test that no query takes > 10 seconds
                queries_results = []
                if queries is not None:
                    number_of_results_per_query = {}
                    for i, row in queries.iterrows():
                        q_id = row['query_id']
                        q_keywords = row['keywords']
                        start_time = time.time()
                        q_n_res, q_res = engine.search(q_keywords)
                        number_of_results_per_query[q_id] = q_n_res
                        end_time = time.time()
                        q_time = end_time - start_time
                        if q_n_res is None or q_res is None or q_n_res < 1 or len(q_res) < 1:
                            logging.error(f"Query {q_id} with keywords '{q_keywords}' returned no results.")
                        else:
                            logging.debug(f"{engine_module} successfully returned {q_n_res} results for query number {q_id}.")
                            invalid_tweet_ids = [doc_id for doc_id in q_res if invalid_tweet_id(doc_id)]
                            if len(invalid_tweet_ids) > 0:
                                logging.error(f"Query  {q_id} returned results that are not valid tweet ids: " + str(
                                    invalid_tweet_ids[:10]))
                            queries_results.extend(
                                [(q_id, str(doc_id)) for doc_id in q_res if not invalid_tweet_id(doc_id)])
                        if q_time > 10:
                            logging.error(f"Query {q_id} with keywords '{q_keywords}' took more than 10 seconds.")
                queries_results = pd.DataFrame(queries_results, columns=['query', 'tweet'])

                # merge query results with labels benchmark
                q_results_labeled = None
                if bench_lbls is not None and len(queries_results) > 0:
                    q_results_labeled = pd.merge(queries_results, bench_lbls,
                                                 on=['query', 'tweet'], how='inner', suffixes=('_result', '_bench'))
                    # q_results_labeled.rename(columns={'y_true': 'label'})

                # test that MAP > 0
                if q_results_labeled is not None:
                    pa5 = []
                    pa10 = []
                    pa50 = []
                    num_relevants = {}
                    print('Module: ' + engine_module)
                    for q in number_of_results_per_query:
                        df2 = bench_lbls[bench_lbls['query'] == q]
                        num_relevants[q] = df2['y_true'].sum()
                        recall = metrics.recall_single(q_results_labeled, num_relevants[q], q)
                        precision = metrics.precision(q_results_labeled, True, q)
                        precision_at5 = metrics.precision_at_n(q_results_labeled, q, 5)
                        precision_at10 = metrics.precision_at_n(q_results_labeled, q, 10)
                        precision_at50 = metrics.precision_at_n(q_results_labeled, q, 50)
                        pa5.append(precision_at5)
                        pa10.append(precision_at10)
                        pa50.append(precision_at50)
                        print('query' + str(q) + ' returned ' + str(
                            number_of_results_per_query[q]) + ' results. ' + ' recall: ' + str(
                            recall) + ' . precision: ' + str(precision) + ' . precision@5: ' + str(precision_at5)
                              + ' . precision@10: ' + str(precision_at10) + ' . precision@50: ' + str(precision_at50))
                    total_precision = metrics.precision(q_results_labeled, False)
                    total_rickall = metrics.recall(q_results_labeled, num_relevants)
                    # TOTAL PRECISION RECALL
                    print('\ntotal precision: ' + str(total_precision) + ' . total recall: ' + str(total_rickall))
                    # PRECISION@5
                    print('avg precision@5: ' + str(statistics.mean(pa5)) + ' , min precision@5: ' + str(min(pa5)) +
                          ' , max precision@5: ' + str(max(pa5)) + ' , median precision@5: ' + str(statistics.median(pa5)))
                    # PRECISION@10
                    print('avg precision@10: ' + str(statistics.mean(pa10)) + ' , min precision@10: ' + str(min(pa10)) +
                          ' , max precision@10: ' + str(max(pa10)) + ' , median precision@10: ' + str(statistics.median(pa10)))
                    # PRECISION@50
                    print('avg precision@pa50: ' + str(statistics.mean(pa50)) + ' , min precision@50: ' + str(min(pa50)) +
                          ' , max precision@50: ' + str(max(pa50)) + ' , median precision@50: ' + str(statistics.median(pa50)))
                    # logging.debug(q_results_labeled.head())
                    results_map = metrics.map(q_results_labeled)
                    logging.debug(f"{engine_module} results have MAP value of {results_map}.")
                    if results_map <= 0 or results_map > 1:
                        logging.error(f'{engine_module} results MAP value is out of range (0,1).')

                    print('MAP: ' + str(results_map))
                    print('------------------------------------------------------')

                # test that the average across queries of precision, 
                # precision@5, precision@10, precision@50, and recall 
                # is in (0,1).

                if engine_module == 'search_engine_best' and \
                        test_file_exists('idx_bench.pkl'):
                    logging.info('idx_bench.pkl found!')
                    engine.load_index('idx_bench.pkl')
                    logging.info('Successfully loaded idx_bench.pkl using search_engine_best.')

            except Exception as e:
                logging.error(f'The following error occured while testing the module {engine_module}.')
                logging.error(e, exc_info=True)

    except Exception as e:
        logging.error(e, exc_info=True)

    run_time = datetime.now() - start
    logging.debug(f'Total runtime was: {run_time}')
