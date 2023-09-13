from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from query_functions import device_query, tag_query
from wtforms.validators import DataRequired
from wtforms import SelectField
from flask_admin.form import Select2Widget

admin = Admin()


class DeviceView(ModelView):
    column_list = ('id', 'device_name', 'ip_address', 'processor_slot',
                   'device_type', 'route', 'connection_size', 'socket_timeout')
    form_columns = ('device_name', 'ip_address', 'processor_slot',
                    'device_type', 'route', 'connection_size', 'socket_timeout')

    form_args = {
        'ip_address': {
            'validators': [DataRequired()]
        }
    }


class TagView(ModelView):
    column_list = ('id', 'tag_name', 'device_tag_name', 'data_type',
                   'description', 'device_id', 'device')
    column_formatters = {
        'device': lambda view, context, model, name: model.device.device_name
    }

    form_columns = ('device', 'tag_name', 'device_tag_name',
                    'data_type', 'description')

    DATA_TYPE_CHOICES = [
        ('int', 'Integer'),
        ('float', 'Float'),
        ('string', 'String'),
        ('bool', 'Boolean')
    ]

    form_overrides = {
        'data_type': SelectField,
    }

    form_args = {
        'device': {
            'query_factory': device_query,
            'get_label': 'device_name',
            'validators': [DataRequired()]
        },
        'device_tag_name': {
            'validators': [DataRequired()]
        },
        'data_type': {
            'label': 'Data Type',
            'widget': Select2Widget(),
            'choices': DATA_TYPE_CHOICES,
            'validators': [DataRequired()]
        }
    }


class PointView(ModelView):
    column_list = ('id', 'timestamp', 'value', 'tag_id',
                   'tag')
    column_formatters = {
        'tag': lambda view, context, model, name: model.tag.tag_name
    }
    form_columns = ('tag', 'value')


class IntegerPointView(PointView):
    form_args = {
        'tag': {
            'query_factory': lambda: tag_query('int'),
            'get_label': 'tag_name',
            'validators': [DataRequired()]
        }
    }


class FloatPointView(PointView):
    form_args = {
        'tag': {
            'query_factory': lambda: tag_query('float'),
            'get_label': 'tag_name',
            'validators': [DataRequired()]
        }
    }


class StringPointView(PointView):
    form_args = {
        'tag': {
            'query_factory': lambda: tag_query('string'),
            'get_label': 'tag_name',
            'validators': [DataRequired()]
        }
    }


class BoolPointView(PointView):
    form_args = {
        'tag': {
            'query_factory': lambda: tag_query('bool'),
            'get_label': 'tag_name',
            'validators': [DataRequired()]
        }
    }
