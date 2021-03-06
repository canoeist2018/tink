# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Cross-language tests for the DeterministicAead primitive."""

from absl.testing import absltest
from absl.testing import parameterized

import tink
from tink import daead
from util import supported_key_types
from util import testing_servers

SUPPORTED_LANGUAGES = testing_servers.SUPPORTED_LANGUAGES_BY_PRIMITIVE['daead']


def setUpModule():
  daead.register()
  testing_servers.start()


def tearDownModule():
  testing_servers.stop()


class DeterministicAeadTest(parameterized.TestCase):

  @parameterized.parameters(
      supported_key_types.test_cases(supported_key_types.DAEAD_KEY_TYPES))
  def test_encrypt_decrypt(self, key_template_name, supported_langs):
    key_template = supported_key_types.KEY_TEMPLATE[key_template_name]
    keyset = testing_servers.new_keyset('java', key_template)
    supported_daeads = [
        testing_servers.deterministic_aead(lang, keyset)
        for lang in supported_langs
    ]
    self.assertNotEmpty(supported_daeads)
    unsupported_daeads = [
        testing_servers.deterministic_aead(lang, keyset)
        for lang in SUPPORTED_LANGUAGES
        if lang not in supported_langs
    ]
    plaintext = (
        b'This is some plaintext message to be encrypted using '
        b'key_template %s.' % key_template_name.encode('utf8'))
    associated_data = (
        b'Some associated data for %s.' % key_template_name.encode('utf8'))
    ciphertext = None
    for p in supported_daeads:
      if ciphertext:
        self.assertEqual(
            ciphertext,
            p.encrypt_deterministically(plaintext, associated_data))
      else:
        ciphertext = p.encrypt_deterministically(plaintext, associated_data)
    for p2 in supported_daeads:
      output = p2.decrypt_deterministically(ciphertext, associated_data)
      self.assertEqual(output, plaintext)
    for p2 in unsupported_daeads:
      with self.assertRaises(tink.TinkError):
        p2.decrypt_deterministically(ciphertext, associated_data)
    for p in unsupported_daeads:
      with self.assertRaises(tink.TinkError):
        p.encrypt_deterministically(b'plaintext', b'associated_data')

if __name__ == '__main__':
  absltest.main()
