from src.validation.validation_pipeline import DataValidationPipeline

if __name__ == '__main__':
    pipeline = DataValidationPipeline()
    results = pipeline.run_validation()
    pipeline.print_summary(results)
    print('Report path:', results.get('report_path'))
