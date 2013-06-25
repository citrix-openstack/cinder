# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright (c) 2013 eNovance , Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
"""Unit tests for image utils."""

from cinder.image import image_utils
from cinder import test
from cinder import utils
import mox
import textwrap


class TestUtils(test.TestCase):
    def setUp(self):
        super(TestUtils, self).setUp()
        self._mox = mox.Mox()
        self.addCleanup(self._mox.UnsetStubs)

    def test_resize_image(self):
        mox = self._mox
        mox.StubOutWithMock(utils, 'execute')

        TEST_IMG_SOURCE = 'boobar.img'
        TEST_IMG_SIZE_IN_GB = 1

        utils.execute('qemu-img', 'resize', TEST_IMG_SOURCE,
                      '%sG' % TEST_IMG_SIZE_IN_GB, run_as_root=False)

        mox.ReplayAll()

        image_utils.resize_image(TEST_IMG_SOURCE, TEST_IMG_SIZE_IN_GB)

        mox.VerifyAll()


class TestExtractTo(test.TestCase):
    def test_extract_to_calls_tar(self):
        mox = self.mox
        mox.StubOutWithMock(utils, 'execute')

        utils.execute(
            'tar', '-xzf', 'archive.tgz', '-C', 'targetpath').AndReturn(
                ('ignored', 'ignored')
            )

        mox.ReplayAll()

        image_utils.TarGz('archive.tgz').extract_to('targetpath')
        mox.VerifyAll()


class TestSetVhdParent(test.TestCase):
    def test_vhd_util_call(self):
        mox = self.mox
        mox.StubOutWithMock(utils, 'execute')

        utils.execute(
            'vhd-util', 'modify', '-n', 'child', '-p', 'parent').AndReturn(
                ('ignored', 'ignored')
            )

        mox.ReplayAll()

        image_utils.set_vhd_parent('child', 'parent')
        mox.VerifyAll()


class TestFixVhdChain(test.TestCase):
    def test_empty_chain(self):
        mox = self.mox
        mox.StubOutWithMock(image_utils, 'set_vhd_parent')

        mox.ReplayAll()
        image_utils.fix_vhd_chain([])

    def test_single_vhd_file_chain(self):
        mox = self.mox
        mox.StubOutWithMock(image_utils, 'set_vhd_parent')

        mox.ReplayAll()
        image_utils.fix_vhd_chain(['0.vhd'])

    def test_chain_with_two_elements(self):
        mox = self.mox
        mox.StubOutWithMock(image_utils, 'set_vhd_parent')

        image_utils.set_vhd_parent('0.vhd', '1.vhd')

        mox.ReplayAll()
        image_utils.fix_vhd_chain(['0.vhd', '1.vhd'])


class TestGetSize(test.TestCase):
    def test_vhd_util_call(self):
        mox = self.mox
        mox.StubOutWithMock(utils, 'execute')

        utils.execute(
            'vhd-util', 'query', '-n', 'vhdfile', '-v').AndReturn(
                ('1024', 'ignored')
            )

        mox.ReplayAll()

        result = image_utils.get_vhd_size('vhdfile')
        mox.VerifyAll()

        self.assertEquals(1024, result)


class TestResize(test.TestCase):
    def test_vhd_util_call(self):
        mox = self.mox
        mox.StubOutWithMock(utils, 'execute')

        utils.execute(
            'vhd-util', 'resize', '-n', 'vhdfile', '-s', '1024',
            '-j', 'journal').AndReturn(('ignored', 'ignored'))

        mox.ReplayAll()

        image_utils.resize_vhd('vhdfile', 1024, 'journal')
        mox.VerifyAll()


class TestCoalesce(test.TestCase):
    def test_vhd_util_call(self):
        mox = self.mox
        mox.StubOutWithMock(utils, 'execute')

        utils.execute(
            'vhd-util', 'coalesce', '-n', 'vhdfile'
            ).AndReturn(('ignored', 'ignored'))

        mox.ReplayAll()

        image_utils.coalesce_vhd('vhdfile')
        mox.VerifyAll()
