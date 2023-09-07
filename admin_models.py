from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

# ModelViews of database classes to view in admin page
admin = Admin()


class DeviceView(ModelView):
    list_columns = ('id', 'device_name', 'ip_address', 'processor_slot',
                    'device_type', 'route', 'connection_size', 'socket_timeout')
    form_columns = ('device_name', 'ip_address', 'processor_slot',
                    'device_type', 'route', 'connection_size', 'socket_timeout')


class TagView(ModelView):
    list_columns = ('id', 'tag_name', 'device_tag_name', 'data_type',
                    'description', 'device_id', 'device')
    form_columns = ('device', 'tag_name', 'device_tag_name',
                    'data_type', 'description')


class PointView(ModelView):
    list_columns = ('id', 'timestamp', 'tag_id',
                    'tag')


class IntegerPointView(ModelView):
    list_columns = ('id', 'timestamp', 'value', 'tag_id',
                    'tag')
    form_columns = ('tag', 'value')


class FloatPointView(ModelView):
    list_columns = ('id', 'timestamp', 'value', 'tag_id',
                    'tag')
    form_columns = ('tag', 'value')


class StringPointView(ModelView):
    list_columns = ('id', 'timestamp', 'value', 'tag_id',
                    'tag')
    form_columns = ('tag', 'value')


class BoolPointView(ModelView):
    list_columns = ('id', 'timestamp', 'value', 'tag_id',
                    'tag')
    form_columns = ('tag', 'value')
