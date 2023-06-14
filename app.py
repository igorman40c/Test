# Мурзин И. - импорт необходимых библиотек для работы с базой данных и передачей результатов по API
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc, desc
import os

# Мурзин И. - настройка экземпляра базы данных и объявление доступа к нему через сервис
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.environ['POSTGRES_USER']}" \
                                        f":{os.environ['POSTGRES_PASSWORD']}" \
                                        f"@{os.environ['POSTGRES_HOST']}:5432/{os.environ['POSTGRES_DB']}"
db = SQLAlchemy(app)


# Мурзин И. - создание таблицы с данными в виде класса, где прописываются названия каждого столбца и формат значений
class Operation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    consume = db.Column(db.String(50))
    start_volume = db.Column(db.Integer)
    unit_measure = db.Column(db.String(50))
    name_employee = db.Column(db.String(50))
    position_employee = db.Column(db.String(50))
    num_taken = db.Column(db.Integer)
    reason = db.Column(db.String(50))
    fin_volume = db.Column(db.Integer)
    date_volume = db.Column(db.String(50))

    def __init__(self, consume, start_volume, unit_measure,
                 name_employee, position_employee, num_taken,
                 reason, fin_volume, date_volume):
        self.consume = consume
        self.start_volume = start_volume
        self.unit_measure = unit_measure
        self.name_employee = name_employee
        self.position_employee = position_employee
        self.num_taken = num_taken
        self.reason = reason
        self.fin_volume = fin_volume
        self.date_volume = date_volume


with app.app_context():
    db.create_all()


# Уразаев А. - реализация функции вывода для пользователя всех операций с расходниками, имеющихся в базе данных
@app.route('/all_operations')
def all_operations():
    try:
        operations = Operation.query.order_by(desc(Operation.date_volume)).all()
        result = []
        for operation in operations:
            data = {
                'id': operation.id,
                'consume': operation.consume,
                'start_volume': operation.start_volume,
                'unit_measure': operation.unit_measure,
                'name_employee': operation.name_employee,
                'position_employee': operation.position_employee,
                'num_taken': operation.num_taken,
                'reason': operation.reason,
                'fin_volume': operation.fin_volume,
                'date_volume': operation.date_volume
            }
            result.append(data)
        return jsonify(result)
    except exc.SQLAlchemyError as e:
        error = str(e)
        return jsonify({'error': error}), 500


# Рязанов И. - реализация функции получения всех операций с расходниками в базе данных по определенным категориям:
# название расходника, единица его измерения, остаток на дату и сама дата
@app.route('/get_volume_consumables')
def get_volume_consumables():
    try:
        operations = Operation.query.order_by(Operation.consume, desc(Operation.date_volume)).all()
        result = []
        for operation in operations:
            data = {
                'consume': operation.consume,
                'unit_measure': operation.unit_measure,
                'fin_volume': operation.fin_volume,
                'date_volume': operation.date_volume
            }
            result.append(data)
        return jsonify(result)
    except exc.SQLAlchemyError as e:
        error = str(e)
        return jsonify({'error': error}), 500


# Пермякова Ю. - реализация функции добавления новой операции с расходниками в базе данных,
# где отдельно присваивается значение каждому ее признаку
@app.route('/add_operation', methods=['POST'])
def add_operation():
    try:
        consume = request.json['consume']
        start_volume = request.json['start_volume']
        unit_measure = request.json['unit_measure']
        name_employee = request.json['name_employee']
        position_employee = request.json['position_employee']
        num_taken = request.json['num_taken']
        reason = request.json['reason']
        fin_volume = request.json['fin_volume']
        date_volume = request.json['date_volume']
        operation = Operation(
            consume=consume, start_volume=start_volume, unit_measure=unit_measure,
            name_employee=name_employee, position_employee=position_employee,
            num_taken=num_taken, reason=reason, fin_volume=fin_volume, date_volume=date_volume)
        db.session.add(operation)
        db.session.commit()
        return jsonify({'message': 'Operation added successfully'})
    except exc.SQLAlchemyError as e:
        error = str(e)
        return jsonify({'error': error}), 500


# Федоренок Е. - реализация функции обновления (замены) характеристик операции с расходниками в базе данных
@app.route('/update_operation/<int:id>', methods=['PUT'])
def update_operation(id):
    try:
        operation = Operation.query.get(id)
        if not operation:
            return jsonify({'error': 'Operation cannot be found'}), 404
        consume = request.json['consume']
        start_volume = request.json['start_volume']
        unit_measure = request.json['unit_measure']
        name_employee = request.json['name_employee']
        position_employee = request.json['position_employee']
        num_taken = request.json['num_taken']
        reason = request.json['reason']
        fin_volume = request.json['fin_volume']
        date_volume = request.json['date_volume']
        operation.consume = consume
        operation.start_volume = start_volume
        operation.unit_measure = unit_measure
        operation.name_employee = name_employee
        operation.position_employee = position_employee
        operation.num_taken = num_taken
        operation.reason = reason
        operation.fin_volume = fin_volume
        operation.date_volume = date_volume
        db.session.commit()
        return jsonify({'message': 'Operation updated successfully'})
    except exc.SQLAlchemyError as e:
        error = str(e)
        return jsonify({'error': error}), 500


# Рязанов И. - реализация функции удаления операции с расходниками в базе данных, а также условие запуска сервиса
@app.route('/delete_operation/<int:id>', methods=['DELETE'])
def delete_operation(id):
    try:
        operation = Operation.query.get(id)
        if not operation:
            return jsonify({'error': 'Operation cannot be found'}), 404
        db.session.delete(operation)
        db.session.commit()
        return jsonify({'message': 'Operation deleted successfully'})
    except exc.SQLAlchemyError as e:
        error = str(e)
        return jsonify({'error': error}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
