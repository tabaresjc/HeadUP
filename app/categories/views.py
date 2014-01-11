from flask.ext.login import login_required
from flask.ext.classy import FlaskView, route


class CategoriesView(FlaskView):
    route_base = '/categories'
    decorators = [login_required]

    def index(self):
        return "ok"

    def get(self, id):
        return "ok"

    @route('/<int:id>', methods=['PUT'])
    @route('/edit/<int:id>', methods=['GET', 'POST'])
    def put(self, id):
        return "ok"

    @route('/<int:id>', methods=['DELETE'])
    @route('/remove/<int:id>', methods=['POST'])
    def delete(self, id):
        return "ok"
