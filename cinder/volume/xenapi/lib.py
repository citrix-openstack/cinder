import contextlib


class XenAPIException(Exception):
    def __init__(self, original_exception):
        super(XenAPIException, self).__init__(str(original_exception))
        self.original_exception = original_exception


class OperationsBase(object):
    def __init__(self, xenapi_session):
        self.session = xenapi_session

    def call_xenapi(self, method, *args):
        return self.session.call_xenapi(method, *args)


class PbdOperations(OperationsBase):
    def get_all(self):
        return self.call_xenapi('PBD.get_all')

    def unplug(self, pbd_ref):
        self.call_xenapi('PBD.unplug', pbd_ref)

    def create(self, host_ref, sr_ref, device_config):
        return self.call_xenapi(
            'PBD.create',
            dict(
                host=host_ref,
                SR=sr_ref,
                device_config=device_config
            )
        )

    def plug(self, pbd_ref):
        self.call_xenapi('PBD.plug', pbd_ref)


class SrOperations(OperationsBase):
    def get_all(self):
        return self.call_xenapi('SR.get_all')

    def get_record(self, sr_ref):
        return self.call_xenapi('SR.get_record', sr_ref)

    def forget(self, sr_ref):
        self.call_xenapi('SR.forget', sr_ref)

    def scan(self, sr_ref):
        self.call_xenapi('SR.scan', sr_ref)

    def create(self, host_ref, device_config, name_label, name_description,
                  sr_type, physical_size=None, content_type=None,
                  shared=False, sm_config=None):
        return self.call_xenapi(
            'SR.create',
            host_ref,
            device_config,
            physical_size or '0',
            name_label or '',
            name_description or '',
            sr_type,
            content_type or '',
            shared,
            sm_config or dict()
        )

    def introduce(self, sr_uuid, name_label, name_description, sr_type,
                     content_type=None, shared=False, sm_config=None):
        return self.call_xenapi(
            'SR.introduce',
            sr_uuid,
            name_label or '',
            name_description or '',
            sr_type,
            content_type or '',
            shared,
            sm_config or dict()
        )


class XenAPISession(object):
    def __init__(self, session, exception_to_convert):
        self._session = session
        self.exception_to_convert = exception_to_convert
        self.handle = self._session.handle
        self.PBD = PbdOperations(self)
        self.SR = SrOperations(self)

    def close(self):
        return self.call_xenapi('logout')

    def call_xenapi(self, method, *args):
        try:
            return self._session.xenapi_request(method, args)
        except self.exception_to_convert as e:
            raise XenAPIException(e)

    def get_pool(self):
        return self.call_xenapi('session.get_pool', self.handle)

    def get_this_host(self):
        return self.call_xenapi('session.get_this_host', self.handle)

    def get_vdis(self):
        return self.call_xenapi('VDI.get_all')

    def get_vdi_record(self, vdi_ref):
        return self.call_xenapi('VDI.get_record', vdi_ref)

    def get_host_record(self, host_ref):
        return self.call_xenapi('host.get_record', host_ref)

    def get_vdi_by_uuid(self, vdi_uuid):
        return self.call_xenapi('VDI.get_by_uuid', vdi_uuid)

    def get_host_by_uuid(self, host_uuid):
        return self.call_xenapi('host.get_by_uuid', host_uuid)

    def create_vdi(self, sr_ref, size, vdi_type,
                   sharable=False, read_only=False, other_config=None):
        return self.call_xenapi('VDI.create',
            dict(
                SR=sr_ref,
                virtual_size=str(size),
                type=vdi_type,
                sharable=sharable,
                read_only=read_only,
                other_config=other_config or dict()
            )
        )

    # Record based operations
    def get_sr_uuid(self, sr_ref):
        return self.SR.get_record(sr_ref)['uuid']

    def get_sr_name_label(self, sr_ref):
        return self.SR.get_record(sr_ref)['name_label']

    def get_sr_name_description(self, sr_ref):
        return self.SR.get_record(sr_ref)['name_description']

    def get_vdi_uuid(self, vdi_ref):
        return self.get_vdi_record(vdi_ref)['uuid']

    def is_nfs_sr(self, sr_ref):
        return self.SR.get_record(sr_ref).get('type') == 'nfs'

    def get_host_uuid(self, host_ref):
        return self.get_host_record(host_ref)['uuid']

    # Compound operations
    def unplug_pbds_and_forget_sr(self, sr_ref):
        sr_rec = self.SR.get_record(sr_ref)
        for pbd_ref in sr_rec.get('PBDs', []):
            self.PBD.unplug(pbd_ref)
        self.SR.forget(sr_ref)

    def create_new_vdi(self, sr_ref, size):
        return self.create_vdi(
                sr_ref,
                size,
                'User',
        )

    # NFS specific
    @contextlib.contextmanager
    def new_sr_on_nfs(self, host_ref, server, serverpath,
                      name_label=None, name_description=None):

        device_config = dict(
            server=server,
            serverpath=serverpath
        )
        name_label = name_label or ''
        name_description = name_description or ''
        sr_type = 'nfs'

        sr_ref = self.SR.create(
            host_ref,
            device_config,
            name_label,
            name_description,
            sr_type,
        )
        yield sr_ref

        self.unplug_pbds_and_forget_sr(sr_ref)

    def plug_nfs_sr(self, host_ref, server, serverpath, sr_uuid,
                    name_label=None, name_description=None):

        device_config = dict(
            server=server,
            serverpath=serverpath
        )
        sr_type = 'nfs'

        sr_ref = self.SR.introduce(
            sr_uuid,
            name_label,
            name_description,
            sr_type,
        )

        pbd_ref = self.PBD.create(
            host_ref,
            sr_ref,
            device_config
        )

        self.PBD.plug(pbd_ref)

        return sr_ref


class ContextAwareSession(XenAPISession):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


def connect(url, user, password):
    import XenAPI
    session = XenAPI.Session(url)
    session.login_with_password(user, password)
    return ContextAwareSession(session, XenAPI.Failure)


class SessionFactory(object):
    def __init__(self, url, user, password):
        self.url = url
        self.user = user
        self.password = password

    def get_session(self):
        return connect(self.url, self.user, self.password)


class NFSBasedVolumeOperations(object):
    def __init__(self, session_factory):
        self._session_factory = session_factory

    def create_volume(self, server, serverpath, size,
                      name=None, description=None):
        with self._session_factory.get_session() as session:
            host_ref = session.get_this_host()
            with session.new_sr_on_nfs(host_ref, server, serverpath,
                                       name, description) as sr_ref:
                vdi_ref = session.create_new_vdi(sr_ref, size)

                return dict(
                    sr_uuid=session.get_sr_uuid(sr_ref),
                    vdi_uuid=session.get_vdi_uuid(vdi_ref)
                )

    def connect_volume(self, host_uuid, server, serverpath, sr_uuid, vdi_uuid):
        with self._session_factory.get_session() as session:
            host_ref = session.get_host_by_uuid(host_uuid)
            sr_ref = session.plug_nfs_sr(
                host_ref,
                server,
                serverpath,
                sr_uuid
            )
            session.SR.scan(sr_ref)
            return session.get_vdi_by_uuid(vdi_uuid)

    def disconnect_volume(self, vdi_ref):
        with self._session_factory.get_session() as session:
            vdi_rec = session.get_vdi_record(vdi_ref)
            sr_ref = vdi_rec['SR']
            session.unplug_pbds_and_forget_sr(sr_ref)
