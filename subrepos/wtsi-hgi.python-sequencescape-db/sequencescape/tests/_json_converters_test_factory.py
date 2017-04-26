import json
import unittest
from typing import Callable, Tuple, Sequence

from sequencescape.models import Model


class _TestJSONEncoder(unittest.TestCase):
    """
    Tests for custom JSON encoders.
    """
    def __init__(self, model_factory: Callable[[], Model], expected_json_properties: Sequence[str], encoder_type: type,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_factory = model_factory
        self.expected_json_properties = expected_json_properties
        self.encoder_type = encoder_type

    def setUp(self):
        self.model = self.model_factory()

    def test_default(self):
        encoded_as_dict = self.encoder_type().default(self.model)
        for property in self.expected_json_properties:
            self.assertIn(property, encoded_as_dict)
        self.assertEqual(len(encoded_as_dict), len(self.expected_json_properties))

    def test_with_json_dumps(self):
        encoded_as_string = json.dumps(self.model, cls=self.encoder_type)
        encoded_as_dict = json.loads(encoded_as_string)
        for property in self.expected_json_properties:
           self.assertIn(property, encoded_as_dict)
        self.assertEqual(len(encoded_as_dict), len(self.expected_json_properties))


class _TestJSONDecoder(unittest.TestCase):
    """
    Tests for custom JSON decoders.
    """
    def __init__(self, model_factory: Callable[[], Model], encoder_type: type, decoder_type: type, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_factory = model_factory
        self.encoder_type = encoder_type
        self.decoder_type = decoder_type

    def setUp(self):
        self.model = self.model_factory()

    def test_decode(self):
        encoded_as_string = json.dumps(self.model, cls=self.encoder_type)
        decoded = self.decoder_type().decode(encoded_as_string)
        self.assertEqual(decoded, self.model)

    def test_decode_parsed(self):
        encoded_as_dict = self.encoder_type().default(self.model)
        decoded = self.decoder_type().decode_parsed(encoded_as_dict)
        self.assertEqual(decoded, self.model)

    def test_with_json_loads(self):
        encoded_as_string = json.dumps(self.model, cls=self.encoder_type)
        decoded = json.loads(encoded_as_string, cls=self.decoder_type)
        self.assertEqual(decoded, self.model)


def create_json_converter_test(model_factory: Callable[[], Model], expected_json_properties: Sequence[str],
                               encoder_type: type, decoder_type: type) -> Tuple[unittest.TestCase, unittest.TestCase]:
    """
    Creates a unit tests for testing a JSON converter.
    :param model_factory: factory that produces models that the converter deals with
    :param expected_json_properties: the properties that are expected to be in the JSON
    :param encoder_type: the JSON encoder type to test
    :param decoder_type: the JSON decoder type to test
    :return: tuple where the first element is a unit test for the encoder and the second is a unit test for the decoder
    """
    encoder_test_class_name = "Test%s" % encoder_type.__name__
    decoder_test_class_name = "Test%s" % decoder_type.__name__

    def init(self, *args, **kwargs):
        if "transplant_class" in str(type(self)):
            # Fix for nosetest, which does some strange subclassing that results in the wrong super been used
            self_type = type(self).mro()[1]
        else:
            self_type = type(self)
        super(self_type, self).__init__(*self._SETUP, *args, **kwargs)

    encoder_test_class = type(
        encoder_test_class_name,
        (_TestJSONEncoder, ),
        {
            "_SETUP": (model_factory, expected_json_properties, encoder_type),
            "__init__": init
        }
    )
    decoder_test_class = type(
        decoder_test_class_name,
        (_TestJSONDecoder, ),
        {
            "_SETUP": (model_factory, encoder_type, decoder_type),
            "__init__": init
        }
    )
    return encoder_test_class, decoder_test_class
