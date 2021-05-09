import configuration
import search_engine_1
import search_engine_best

if __name__ == '__main__':
    bench_data_path = 'data/benchmark_data_train.snappy.parquet'
    config = configuration.ConfigClass()
    se = search_engine_1.SearchEngine(config)
    se.build_index_from_parquet(bench_data_path)
    n_res, res = se.search('bioweapon')
