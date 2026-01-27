from .base_builder import BaseECFBuilder
from .builders import (
    ECF31Builder, ECF32Builder, ECF33Builder, ECF34Builder,
    ECF41Builder, ECF43Builder, ECF44Builder, ECF45Builder, ECF46Builder, ECF47Builder
)

class ECFBuilderManager:
    @staticmethod
    def get_builder(data_json):
        try:
            tipo_ecf = int(data_json['Encabezado']['IdDoc']['TipoeCF'])
        except (KeyError, ValueError):
            # Default to base if type missing (shouldn't happen in valid data)
            return BaseECFBuilder(data_json)

        builders = {
            31: ECF31Builder,
            32: ECF32Builder,
            33: ECF33Builder,
            34: ECF34Builder,
            41: ECF41Builder,
            43: ECF43Builder,
            44: ECF44Builder,
            45: ECF45Builder,
            46: ECF46Builder,
            47: ECF47Builder,
        }

        builder_class = builders.get(tipo_ecf, BaseECFBuilder)
        return builder_class(data_json)
