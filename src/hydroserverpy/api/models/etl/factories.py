from .extractors import HTTPExtractor, LocalFileExtractor
from .transformers import JSONTransformer, CSVTransformer
from .loaders import HydroServerLoader
from .etl_configuration import ExtractorConfig, TransformerConfig, LoaderConfig

EXTRACTORS = {"HTTP": HTTPExtractor, "local": LocalFileExtractor}
TRANSFORMERS = {"JSON": JSONTransformer, "CSV": CSVTransformer}
LOADERS = {"HydroServer": HydroServerLoader}


def extractor_factory(settings: ExtractorConfig):
    cls = EXTRACTORS[settings.type]
    return cls(settings)


def transformer_factory(settings: TransformerConfig):
    cls = TRANSFORMERS[settings.type]
    return cls(settings)


def loader_factory(settings: LoaderConfig, auth_context, data_source_id: str):
    cls = LOADERS[settings.type]
    return cls(auth_context, data_source_id)
