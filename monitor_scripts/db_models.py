from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# Device Model
class Device(db.Model):
    __tablename__ = 'devices'
    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, nullable=False)
    device_name = db.Column(db.String(150), unique=True, nullable=False)
    ip_address = db.Column(db.String(150))
    processor_slot = db.Column(db.Integer)
    device_type = db.Column(db.String(150), nullable=True)
    route = db.Column(db.Integer, nullable=True)
    connection_size = db.Column(db.Integer, nullable=True)
    socket_timeout = db.Column(db.Float, nullable=True)
    # Define the one-to-many relationship with tags
    tags = db.relationship("Tag", back_populates="device")

    def __init__(self, device_name, ip_address, processor_slot=0, device_type=None, route=None, connection_size=None, socket_timeout=None):
        super().__init__()
        self.device_name = device_name
        self.ip_address = ip_address
        self.processor_slot = processor_slot
        self.device_type = device_type
        self.route = route
        self.connection_size = connection_size
        self.socket_timeout = socket_timeout

    def __hash__(self):
        return hash((self.device_name, self.ip_address))

    def __eq__(self, other):
        if isinstance(other, Device):
            return (self.device_name == other.device_name and self.ip_address == other.ip_address)
        return False


# Tag Model
class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, nullable=False)
    tag_name = db.Column(db.String(150), unique=True, nullable=False)
    device_tag_name = db.Column(db.String(150))
    data_type = db.Column(db.String(150))
    description = db.Column(db.Text)
    deadband = db.Column(db.Float)
    history_type = db.Column(db.String(150))

    # Foreign Key and Relationship with Devices
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'))
    device = db.relationship("Device", back_populates="tags")

    def __init__(self, device, tag_name, device_tag_name, data_type=0, description=None, deadband=0):
        super().__init__()
        self.device = device
        self.tag_name = tag_name
        self.device_tag_name = device_tag_name
        self.data_type = data_type
        self.description = description
        self.deadband = deadband

    def __hash__(self):
        return hash((self.tag_name, self.data_type))

    def __eq__(self, other):
        if isinstance(other, Tag):
            return (self.tag_name == other.tag_name and self.data_type == other.data_type)
        return False


class Point(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, nullable=False)
    timestamp = db.Column(
        db.TIMESTAMP, server_default=db.func.current_timestamp())


class IntegerPoint(Point):
    __tablename__ = 'integer_points'
    value = db.Column(db.Integer)
    # Foreign Key and Relationship with Tags
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'))
    tag = db.relationship("Tag", backref="integer_points", single_parent=True)

    def __init__(self, tag, value):
        super().__init__()
        self.tag = tag
        self.value = value


class FloatPoint(Point):
    __tablename__ = 'float_points'
    value = db.Column(db.Float)
    # Foreign Key and Relationship with Tags
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'))
    tag = db.relationship("Tag", backref="float_points", single_parent=True)

    def __init__(self, tag, value):
        super().__init__()
        self.tag = tag
        self.value = value


class StringPoint(Point):
    __tablename__ = 'string_points'
    value = db.Column(db.Text)
    # Foreign Key and Relationship with Tags
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'))
    tag = db.relationship("Tag", backref="string_points", single_parent=True)

    def __init__(self, tag, value):
        super.__init__()
        self.tag = tag
        self.value = value


class BoolPoint(Point):
    __tablename__ = 'bool_points'
    value = db.Column(db.Boolean)
    # Foreign Key and Relationship with Tags
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'))
    tag = db.relationship("Tag", backref="bool_points", single_parent=True)

    def __init__(self, tag, value):
        super.__init__()
        self.tag = tag
        self.value = value
