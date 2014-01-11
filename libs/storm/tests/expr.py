#
# Copyright (c) 2006, 2007 Canonical
#
# Written by Gustavo Niemeyer <gustavo@niemeyer.net>
#
# This file is part of Storm Object Relational Mapper.
#
# Storm is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation; either version 2.1 of
# the License, or (at your option) any later version.
#
# Storm is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
from decimal import Decimal

from tests.helper import TestHelper

from storm.variables import *
from storm.expr import *


class Func1(NamedFunc):
    name = "func1"

class Func2(NamedFunc):
    name = "func2"

# Create columnN, tableN, and elemN variables.
for i in range(10):
    for name in ["column", "elem"]:
        exec "%s%d = SQLToken('%s%d')" % (name, i, name, i)
    for name in ["table"]:
        exec "%s%d = '%s %d'" % (name, i, name, i)


class TrackContext(FromExpr):
    context = None

@compile.when(TrackContext)
def compile_track_context(compile, expr, state):
    expr.context = state.context
    return ""

def track_contexts(n):
    return [TrackContext() for i in range(n)]


class ExprTest(TestHelper):

    def test_select_default(self):
        expr = Select(())
        self.assertEquals(expr.columns, ())
        self.assertEquals(expr.where, Undef)
        self.assertEquals(expr.tables, Undef)
        self.assertEquals(expr.default_tables, Undef)
        self.assertEquals(expr.order_by, Undef)
        self.assertEquals(expr.group_by, Undef)
        self.assertEquals(expr.limit, Undef)
        self.assertEquals(expr.offset, Undef)
        self.assertEquals(expr.distinct, False)

    def test_select_constructor(self):
        objects = [object() for i in range(9)]
        expr = Select(*objects)
        self.assertEquals(expr.columns, objects[0])
        self.assertEquals(expr.where, objects[1])
        self.assertEquals(expr.tables, objects[2])
        self.assertEquals(expr.default_tables, objects[3])
        self.assertEquals(expr.order_by, objects[4])
        self.assertEquals(expr.group_by, objects[5])
        self.assertEquals(expr.limit, objects[6])
        self.assertEquals(expr.offset, objects[7])
        self.assertEquals(expr.distinct, objects[8])

    def test_insert_default(self):
        expr = Insert(None)
        self.assertEquals(expr.map, None)
        self.assertEquals(expr.table, Undef)
        self.assertEquals(expr.default_table, Undef)
        self.assertEquals(expr.primary_columns, Undef)
        self.assertEquals(expr.primary_variables, Undef)

    def test_insert_constructor(self):
        objects = [object() for i in range(5)]
        expr = Insert(*objects)
        self.assertEquals(expr.map, objects[0])
        self.assertEquals(expr.table, objects[1])
        self.assertEquals(expr.default_table, objects[2])
        self.assertEquals(expr.primary_columns, objects[3])
        self.assertEquals(expr.primary_variables, objects[4])

    def test_update_default(self):
        expr = Update(None)
        self.assertEquals(expr.map, None)
        self.assertEquals(expr.where, Undef)
        self.assertEquals(expr.table, Undef)
        self.assertEquals(expr.default_table, Undef)

    def test_update_constructor(self):
        objects = [object() for i in range(4)]
        expr = Update(*objects)
        self.assertEquals(expr.map, objects[0])
        self.assertEquals(expr.where, objects[1])
        self.assertEquals(expr.table, objects[2])
        self.assertEquals(expr.default_table, objects[3])

    def test_delete_default(self):
        expr = Delete()
        self.assertEquals(expr.where, Undef)
        self.assertEquals(expr.table, Undef)

    def test_delete_constructor(self):
        objects = [object() for i in range(3)]
        expr = Delete(*objects)
        self.assertEquals(expr.where, objects[0])
        self.assertEquals(expr.table, objects[1])
        self.assertEquals(expr.default_table, objects[2])

    def test_and(self):
        expr = And(elem1, elem2, elem3)
        self.assertEquals(expr.exprs, (elem1, elem2, elem3))

    def test_or(self):
        expr = Or(elem1, elem2, elem3)
        self.assertEquals(expr.exprs, (elem1, elem2, elem3))

    def test_column_default(self):
        expr = Column()
        self.assertEquals(expr.name, Undef)
        self.assertEquals(expr.table, Undef)
        self.assertIdentical(expr.compile_cache, None)

        # Test for identity. We don't want False there.
        self.assertTrue(expr.primary is 0)

        self.assertEquals(expr.variable_factory, Variable)

    def test_column_constructor(self):
        objects = [object() for i in range(3)]
        objects.insert(2, True)
        expr = Column(*objects)
        self.assertEquals(expr.name, objects[0])
        self.assertEquals(expr.table, objects[1])

        # Test for identity. We don't want True there either.
        self.assertTrue(expr.primary is 1)

        self.assertEquals(expr.variable_factory, objects[3])

    def test_func(self):
        expr = Func("myfunc", elem1, elem2)
        self.assertEquals(expr.name, "myfunc")
        self.assertEquals(expr.args, (elem1, elem2))

    def test_named_func(self):
        class MyFunc(NamedFunc):
            name = "myfunc"
        expr = MyFunc(elem1, elem2)
        self.assertEquals(expr.name, "myfunc")
        self.assertEquals(expr.args, (elem1, elem2))

    def test_like(self):
        expr = Like(elem1, elem2)
        self.assertEquals(expr.expr1, elem1)
        self.assertEquals(expr.expr2, elem2)

    def test_like_escape(self):
        expr = Like(elem1, elem2, elem3)
        self.assertEquals(expr.expr1, elem1)
        self.assertEquals(expr.expr2, elem2)
        self.assertEquals(expr.escape, elem3)

    def test_like_case(self):
        expr = Like(elem1, elem2, elem3)
        self.assertEquals(expr.case_sensitive, None)
        expr = Like(elem1, elem2, elem3, True)
        self.assertEquals(expr.case_sensitive, True)
        expr = Like(elem1, elem2, elem3, False)
        self.assertEquals(expr.case_sensitive, False)

    def test_startswith(self):
        expr = Func1()
        self.assertRaises(ExprError, expr.startswith, "not a unicode string")

        like_expr = expr.startswith(u"abc!!_%")
        self.assertTrue(isinstance(like_expr, Like))
        self.assertTrue(like_expr.expr1 is expr)
        self.assertEquals(like_expr.expr2, u"abc!!!!!_!%%")
        self.assertEquals(like_expr.escape, u"!")

    def test_endswith(self):
        expr = Func1()
        self.assertRaises(ExprError, expr.startswith, "not a unicode string")

        like_expr = expr.endswith(u"abc!!_%")
        self.assertTrue(isinstance(like_expr, Like))
        self.assertTrue(like_expr.expr1 is expr)
        self.assertEquals(like_expr.expr2, u"%abc!!!!!_!%")
        self.assertEquals(like_expr.escape, u"!")

    def test_contains_string(self):
        expr = Func1()
        self.assertRaises(
            ExprError, expr.contains_string, "not a unicode string")

        like_expr = expr.contains_string(u"abc!!_%")
        self.assertTrue(isinstance(like_expr, Like))
        self.assertTrue(like_expr.expr1 is expr)
        self.assertEquals(like_expr.expr2, u"%abc!!!!!_!%%")
        self.assertEquals(like_expr.escape, u"!")

    def test_eq(self):
        expr = Eq(elem1, elem2)
        self.assertEquals(expr.expr1, elem1)
        self.assertEquals(expr.expr2, elem2)

    def test_sql_default(self):
        expr = SQL(None)
        self.assertEquals(expr.expr, None)
        self.assertEquals(expr.params, Undef)
        self.assertEquals(expr.tables, Undef)

    def test_sql_constructor(self):
        objects = [object() for i in range(3)]
        expr = SQL(*objects)
        self.assertEquals(expr.expr, objects[0])
        self.assertEquals(expr.params, objects[1])
        self.assertEquals(expr.tables, objects[2])

    def test_join_expr_right(self):
        expr = JoinExpr(None)
        self.assertEquals(expr.right, None)
        self.assertEquals(expr.left, Undef)
        self.assertEquals(expr.on, Undef)

    def test_join_expr_on(self):
        on = Expr()
        expr = JoinExpr(None, on)
        self.assertEquals(expr.right, None)
        self.assertEquals(expr.left, Undef)
        self.assertEquals(expr.on, on)

    def test_join_expr_on_keyword(self):
        on = Expr()
        expr = JoinExpr(None, on=on)
        self.assertEquals(expr.right, None)
        self.assertEquals(expr.left, Undef)
        self.assertEquals(expr.on, on)

    def test_join_expr_on_invalid(self):
        on = Expr()
        self.assertRaises(ExprError, JoinExpr, None, on, None)

    def test_join_expr_right_left(self):
        objects = [object() for i in range(2)]
        expr = JoinExpr(*objects)
        self.assertEquals(expr.left, objects[0])
        self.assertEquals(expr.right, objects[1])
        self.assertEquals(expr.on, Undef)

    def test_join_expr_right_left_on(self):
        objects = [object() for i in range(3)]
        expr = JoinExpr(*objects)
        self.assertEquals(expr.left, objects[0])
        self.assertEquals(expr.right, objects[1])
        self.assertEquals(expr.on, objects[2])

    def test_join_expr_right_join(self):
        join = JoinExpr(None)
        expr = JoinExpr(None, join)
        self.assertEquals(expr.right, join)
        self.assertEquals(expr.left, None)
        self.assertEquals(expr.on, Undef)

    def test_table(self):
        objects = [object() for i in range(1)]
        expr = Table(*objects)
        self.assertEquals(expr.name, objects[0])

    def test_alias_default(self):
        expr = Alias(None)
        self.assertEquals(expr.expr, None)
        self.assertTrue(isinstance(expr.name, str))

    def test_alias_constructor(self):
        objects = [object() for i in range(2)]
        expr = Alias(*objects)
        self.assertEquals(expr.expr, objects[0])
        self.assertEquals(expr.name, objects[1])

    def test_union(self):
        expr = Union(elem1, elem2, elem3)
        self.assertEquals(expr.exprs, (elem1, elem2, elem3))

    def test_union_with_kwargs(self):
        expr = Union(elem1, elem2, all=True, order_by=(), limit=1, offset=2)
        self.assertEquals(expr.exprs, (elem1, elem2))
        self.assertEquals(expr.all, True)
        self.assertEquals(expr.order_by, ())
        self.assertEquals(expr.limit, 1)
        self.assertEquals(expr.offset, 2)

    def test_union_collapse(self):
        expr = Union(Union(elem1, elem2), elem3)
        self.assertEquals(expr.exprs, (elem1, elem2, elem3))

        # Only first expression is collapsed.
        expr = Union(elem1, Union(elem2, elem3))
        self.assertEquals(expr.exprs[0], elem1)
        self.assertTrue(isinstance(expr.exprs[1], Union))

        # Don't collapse if all is different.
        expr = Union(Union(elem1, elem2, all=True), elem3)
        self.assertTrue(isinstance(expr.exprs[0], Union))
        expr = Union(Union(elem1, elem2), elem3, all=True)
        self.assertTrue(isinstance(expr.exprs[0], Union))
        expr = Union(Union(elem1, elem2, all=True), elem3, all=True)
        self.assertEquals(expr.exprs, (elem1, elem2, elem3))

        # Don't collapse if limit or offset are set.
        expr = Union(Union(elem1, elem2, limit=1), elem3)
        self.assertTrue(isinstance(expr.exprs[0], Union))
        expr = Union(Union(elem1, elem2, offset=3), elem3)
        self.assertTrue(isinstance(expr.exprs[0], Union))

        # Don't collapse other set expressions.
        expr = Union(Except(elem1, elem2), elem3)
        self.assertTrue(isinstance(expr.exprs[0], Except))
        expr = Union(Intersect(elem1, elem2), elem3)
        self.assertTrue(isinstance(expr.exprs[0], Intersect))

    def test_except(self):
        expr = Except(elem1, elem2, elem3)
        self.assertEquals(expr.exprs, (elem1, elem2, elem3))

    def test_except_with_kwargs(self):
        expr = Except(elem1, elem2, all=True, order_by=(), limit=1, offset=2)
        self.assertEquals(expr.exprs, (elem1, elem2))
        self.assertEquals(expr.all, True)
        self.assertEquals(expr.order_by, ())
        self.assertEquals(expr.limit, 1)
        self.assertEquals(expr.offset, 2)

    def test_except_collapse(self):
        expr = Except(Except(elem1, elem2), elem3)
        self.assertEquals(expr.exprs, (elem1, elem2, elem3))

        # Only first expression is collapsed.
        expr = Except(elem1, Except(elem2, elem3))
        self.assertEquals(expr.exprs[0], elem1)
        self.assertTrue(isinstance(expr.exprs[1], Except))

        # Don't collapse if all is different.
        expr = Except(Except(elem1, elem2, all=True), elem3)
        self.assertTrue(isinstance(expr.exprs[0], Except))
        expr = Except(Except(elem1, elem2), elem3, all=True)
        self.assertTrue(isinstance(expr.exprs[0], Except))
        expr = Except(Except(elem1, elem2, all=True), elem3, all=True)
        self.assertEquals(expr.exprs, (elem1, elem2, elem3))

        # Don't collapse if limit or offset are set.
        expr = Except(Except(elem1, elem2, limit=1), elem3)
        self.assertTrue(isinstance(expr.exprs[0], Except))
        expr = Except(Except(elem1, elem2, offset=3), elem3)
        self.assertTrue(isinstance(expr.exprs[0], Except))

        # Don't collapse other set expressions.
        expr = Except(Union(elem1, elem2), elem3)
        self.assertTrue(isinstance(expr.exprs[0], Union))
        expr = Except(Intersect(elem1, elem2), elem3)
        self.assertTrue(isinstance(expr.exprs[0], Intersect))

    def test_intersect(self):
        expr = Intersect(elem1, elem2, elem3)
        self.assertEquals(expr.exprs, (elem1, elem2, elem3))

    def test_intersect_with_kwargs(self):
        expr = Intersect(
            elem1, elem2, all=True, order_by=(), limit=1, offset=2)
        self.assertEquals(expr.exprs, (elem1, elem2))
        self.assertEquals(expr.all, True)
        self.assertEquals(expr.order_by, ())
        self.assertEquals(expr.limit, 1)
        self.assertEquals(expr.offset, 2)

    def test_intersect_collapse(self):
        expr = Intersect(Intersect(elem1, elem2), elem3)
        self.assertEquals(expr.exprs, (elem1, elem2, elem3))

        # Only first expression is collapsed.
        expr = Intersect(elem1, Intersect(elem2, elem3))
        self.assertEquals(expr.exprs[0], elem1)
        self.assertTrue(isinstance(expr.exprs[1], Intersect))

        # Don't collapse if all is different.
        expr = Intersect(Intersect(elem1, elem2, all=True), elem3)
        self.assertTrue(isinstance(expr.exprs[0], Intersect))
        expr = Intersect(Intersect(elem1, elem2), elem3, all=True)
        self.assertTrue(isinstance(expr.exprs[0], Intersect))
        expr = Intersect(Intersect(elem1, elem2, all=True), elem3, all=True)
        self.assertEquals(expr.exprs, (elem1, elem2, elem3))

        # Don't collapse if limit or offset are set.
        expr = Intersect(Intersect(elem1, elem2, limit=1), elem3)
        self.assertTrue(isinstance(expr.exprs[0], Intersect))
        expr = Intersect(Intersect(elem1, elem2, offset=3), elem3)
        self.assertTrue(isinstance(expr.exprs[0], Intersect))

        # Don't collapse other set expressions.
        expr = Intersect(Union(elem1, elem2), elem3)
        self.assertTrue(isinstance(expr.exprs[0], Union))
        expr = Intersect(Except(elem1, elem2), elem3)
        self.assertTrue(isinstance(expr.exprs[0], Except))

    def test_auto_tables(self):
        expr = AutoTables(elem1, [elem2])
        self.assertEquals(expr.expr, elem1)
        self.assertEquals(expr.tables, [elem2])

    def test_sequence(self):
        expr = Sequence(elem1)
        self.assertEquals(expr.name, elem1)


class StateTest(TestHelper):

    def setUp(self):
        TestHelper.setUp(self)
        self.state = State()

    def test_attrs(self):
        self.assertEquals(self.state.parameters, [])
        self.assertEquals(self.state.auto_tables, [])
        self.assertEquals(self.state.context, None)

    def test_push_pop(self):
        self.state.parameters.extend([1, 2])
        self.state.push("parameters", [])
        self.assertEquals(self.state.parameters, [])
        self.state.pop()
        self.assertEquals(self.state.parameters, [1, 2])
        self.state.push("parameters")
        self.assertEquals(self.state.parameters, [1, 2])
        self.state.parameters.append(3)
        self.assertEquals(self.state.parameters, [1, 2, 3])
        self.state.pop()
        self.assertEquals(self.state.parameters, [1, 2])

    def test_push_pop_unexistent(self):
        self.state.push("nonexistent")
        self.assertEquals(self.state.nonexistent, None)
        self.state.nonexistent = "something"
        self.state.pop()
        self.assertEquals(self.state.nonexistent, None)


class CompileTest(TestHelper):

    def test_simple_inheritance(self):
        custom_compile = compile.create_child()
        statement = custom_compile(Func1())
        self.assertEquals(statement, "func1()")

    def test_customize(self):
        custom_compile = compile.create_child()
        @custom_compile.when(type(None))
        def compile_none(compile, state, expr):
            return "None"
        statement = custom_compile(Func1(None))
        self.assertEquals(statement, "func1(None)")

    def test_customize_inheritance(self):
        class C(object): pass
        compile_parent = Compile()
        compile_child = compile_parent.create_child()

        @compile_parent.when(C)
        def compile_in_parent(compile, state, expr):
            return "parent"
        statement = compile_child(C())
        self.assertEquals(statement, "parent")

        @compile_child.when(C)
        def compile_in_child(compile, state, expr):
            return "child"
        statement = compile_child(C())
        self.assertEquals(statement, "child")

    def test_precedence(self):
        for i in range(10):
            exec "e%d = SQLRaw('%d')" % (i, i)
        expr = And(e1, Or(e2, e3),
                   Add(e4, Mul(e5, Sub(e6, Div(e7, Div(e8, e9))))))
        statement = compile(expr)
        self.assertEquals(statement, "1 AND (2 OR 3) AND 4+5*(6-7/(8/9))")

        expr = Func1(Select(Count()), [Select(Count())])
        statement = compile(expr)
        self.assertEquals(statement,
                          "func1((SELECT COUNT(*)), (SELECT COUNT(*)))")

    def test_get_precedence(self):
        self.assertTrue(compile.get_precedence(Or) <
                        compile.get_precedence(And))
        self.assertTrue(compile.get_precedence(Add) <
                        compile.get_precedence(Mul))
        self.assertTrue(compile.get_precedence(Sub) <
                        compile.get_precedence(Div))

    def test_customize_precedence(self):
        expr = And(elem1, Or(elem2, elem3))
        custom_compile = compile.create_child()
        custom_compile.set_precedence(10, And)

        custom_compile.set_precedence(11, Or)
        statement = custom_compile(expr)
        self.assertEquals(statement, "elem1 AND elem2 OR elem3")

        custom_compile.set_precedence(10, Or)
        statement = custom_compile(expr)
        self.assertEquals(statement, "elem1 AND elem2 OR elem3")

        custom_compile.set_precedence(9, Or)
        statement = custom_compile(expr)
        self.assertEquals(statement, "elem1 AND (elem2 OR elem3)")

    def test_customize_precedence_inheritance(self):
        compile_parent = compile.create_child()
        compile_child = compile_parent.create_child()

        expr = And(elem1, Or(elem2, elem3))

        compile_parent.set_precedence(10, And)

        compile_parent.set_precedence(11, Or)
        self.assertEquals(compile_child.get_precedence(Or), 11)
        self.assertEquals(compile_parent.get_precedence(Or), 11)
        statement = compile_child(expr)
        self.assertEquals(statement, "elem1 AND elem2 OR elem3")

        compile_parent.set_precedence(10, Or)
        self.assertEquals(compile_child.get_precedence(Or), 10)
        self.assertEquals(compile_parent.get_precedence(Or), 10)
        statement = compile_child(expr)
        self.assertEquals(statement, "elem1 AND elem2 OR elem3")

        compile_child.set_precedence(9, Or)
        self.assertEquals(compile_child.get_precedence(Or), 9)
        self.assertEquals(compile_parent.get_precedence(Or), 10)
        statement = compile_child(expr)
        self.assertEquals(statement, "elem1 AND (elem2 OR elem3)")

    def test_compile_sequence(self):
        expr = [elem1, Func1(), (Func2(), None)]
        statement = compile(expr)
        self.assertEquals(statement, "elem1, func1(), func2(), NULL")

    def test_compile_invalid(self):
        self.assertRaises(CompileError, compile, object())
        self.assertRaises(CompileError, compile, [object()])

    def test_str(self):
        state = State()
        statement = compile("str", state)
        self.assertEquals(statement, "?")
        self.assertVariablesEqual(state.parameters, [RawStrVariable("str")])

    def test_unicode(self):
        state = State()
        statement = compile(u"str", state)
        self.assertEquals(statement, "?")
        self.assertVariablesEqual(state.parameters, [UnicodeVariable(u"str")])

    def test_int(self):
        state = State()
        statement = compile(1, state)
        self.assertEquals(statement, "?")
        self.assertVariablesEqual(state.parameters, [IntVariable(1)])

    def test_long(self):
        state = State()
        statement = compile(1L, state)
        self.assertEquals(statement, "?")
        self.assertVariablesEqual(state.parameters, [IntVariable(1)])

    def test_bool(self):
        state = State()
        statement = compile(True, state)
        self.assertEquals(statement, "?")
        self.assertVariablesEqual(state.parameters, [BoolVariable(1)])

    def test_float(self):
        state = State()
        statement = compile(1.1, state)
        self.assertEquals(statement, "?")
        self.assertVariablesEqual(state.parameters, [FloatVariable(1.1)])

    def test_decimal(self):
        state = State()
        statement = compile(Decimal("1.1"), state)
        self.assertEquals(statement, "?")
        self.assertVariablesEqual(
            state.parameters, [DecimalVariable(Decimal("1.1"))])

    def test_datetime(self):
        dt = datetime(1977, 5, 4, 12, 34)
        state = State()
        statement = compile(dt, state)
        self.assertEquals(statement, "?")
        self.assertVariablesEqual(state.parameters, [DateTimeVariable(dt)])

    def test_date(self):
        d = date(1977, 5, 4)
        state = State()
        statement = compile(d, state)
        self.assertEquals(statement, "?")
        self.assertVariablesEqual(state.parameters, [DateVariable(d)])

    def test_time(self):
        t = time(12, 34)
        state = State()
        statement = compile(t, state)
        self.assertEquals(statement, "?")
        self.assertVariablesEqual(state.parameters, [TimeVariable(t)])

    def test_timedelta(self):
        td = timedelta(days=1, seconds=2, microseconds=3)
        state = State()
        statement = compile(td, state)
        self.assertEquals(statement, "?")
        self.assertVariablesEqual(state.parameters, [TimeDeltaVariable(td)])

    def test_none(self):
        state = State()
        statement = compile(None, state)
        self.assertEquals(statement, "NULL")
        self.assertEquals(state.parameters, [])

    def test_select(self):
        expr = Select([column1, column2])
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "SELECT column1, column2")
        self.assertEquals(state.parameters, [])

    def test_select_distinct(self):
        expr = Select([column1, column2], Undef, [table1], distinct=True)
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement,
                          'SELECT DISTINCT column1, column2 FROM "table 1"')
        self.assertEquals(state.parameters, [])

    def test_select_distinct_on(self):
        expr = Select([column1, column2], Undef, [table1],
                      distinct=[column2, column1])
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement,
                          'SELECT DISTINCT ON (column2, column1) '
                          'column1, column2 FROM "table 1"')
        self.assertEquals(state.parameters, [])

    def test_select_where(self):
        expr = Select([column1, Func1()],
                      Func1(),
                      [table1, Func1()],
                      order_by=[column2, Func1()],
                      group_by=[column3, Func1()],
                      limit=3, offset=4)
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, 'SELECT column1, func1() '
                                     'FROM "table 1", func1() '
                                     'WHERE func1() '
                                     'GROUP BY column3, func1() '
                                     'ORDER BY column2, func1() '
                                     'LIMIT 3 OFFSET 4')
        self.assertEquals(state.parameters, [])

    def test_select_join_where(self):
        expr = Select(column1,
                      Func1() == "value1",
                      Join(table1, Func2() == "value2"))
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, 'SELECT column1 FROM '
                                     'JOIN "table 1" ON func2() = ? '
                                     'WHERE func1() = ?')
        self.assertEquals([variable.get() for variable in state.parameters],
                          ["value2", "value1"])

    def test_select_auto_table(self):
        expr = Select(Column(column1, table1),
                      Column(column2, table2) == 1),
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, 'SELECT "table 1".column1 '
                                     'FROM "table 1", "table 2" '
                                     'WHERE "table 2".column2 = ?')
        self.assertVariablesEqual(state.parameters, [Variable(1)])

    def test_select_auto_table_duplicated(self):
        expr = Select(Column(column1, table1),
                      Column(column2, table1) == 1),
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, 'SELECT "table 1".column1 '
                                     'FROM "table 1" WHERE '
                                     '"table 1".column2 = ?')
        self.assertVariablesEqual(state.parameters, [Variable(1)])

    def test_select_auto_table_default(self):
        expr = Select(Column(column1),
                      Column(column2) == 1,
                      default_tables=table1),
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, 'SELECT column1 FROM "table 1" '
                                     'WHERE column2 = ?')
        self.assertVariablesEqual(state.parameters, [Variable(1)])

    def test_select_auto_table_default_with_joins(self):
        expr = Select(Column(column1),
                      default_tables=[table1, Join(table2)]),
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, 'SELECT column1 '
                                     'FROM "table 1" JOIN "table 2"')
        self.assertEquals(state.parameters, [])

    def test_select_auto_table_unknown(self):
        statement = compile(Select(elem1))
        self.assertEquals(statement, "SELECT elem1")

    def test_select_auto_table_sub(self):
        col1 = Column(column1, table1)
        col2 = Column(column2, table2)
        expr = Select(col1, In(elem1, Select(col2, col1 == col2, col2.table)))
        statement = compile(expr)
        self.assertEquals(statement,
                          'SELECT "table 1".column1 FROM "table 1" WHERE '
                          'elem1 IN (SELECT "table 2".column2 FROM "table 2" '
                          'WHERE "table 1".column1 = "table 2".column2)')

    def test_select_join(self):
        expr = Select([column1, Func1()], Func1(),
                      [table1, Join(table2), Join(table3)])
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, 'SELECT column1, func1() '
                                     'FROM "table 1" JOIN "table 2"'
                                     ' JOIN "table 3" '
                                     'WHERE func1()')
        self.assertEquals(state.parameters, [])

    def test_select_join_right_left(self):
        expr = Select([column1, Func1()], Func1(),
                      [table1, Join(table2, table3)])
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, 'SELECT column1, func1() '
                                     'FROM "table 1", "table 2" '
                                     'JOIN "table 3" WHERE func1()')
        self.assertEquals(state.parameters, [])

    def test_select_with_strings(self):
        expr = Select(column1, "1 = 2", table1, order_by="column1",
                      group_by="column2")
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, 'SELECT column1 FROM "table 1" '
                                     'WHERE 1 = 2 GROUP BY column2 '
                                     'ORDER BY column1')
        self.assertEquals(state.parameters, [])

    def test_select_with_unicode(self):
        expr = Select(column1, u"1 = 2", table1, order_by=u"column1",
                      group_by=[u"column2"])
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, 'SELECT column1 FROM "table 1" '
                                     'WHERE 1 = 2 GROUP BY column2 '
                                     'ORDER BY column1')
        self.assertEquals(state.parameters, [])

    def test_select_having(self):
        expr = Select(column1, tables=table1, order_by=u"column1",
                      group_by=[u"column2"], having=u"1 = 2")
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, 'SELECT column1 FROM "table 1" '
                                     'GROUP BY column2 HAVING 1 = 2 '
                                     'ORDER BY column1')
        self.assertEquals(state.parameters, [])

    def test_select_contexts(self):
        column, where, table, order_by, group_by = track_contexts(5)
        expr = Select(column, where, table,
                      order_by=order_by, group_by=group_by)
        compile(expr)
        self.assertEquals(column.context, COLUMN)
        self.assertEquals(where.context, EXPR)
        self.assertEquals(table.context, TABLE)
        self.assertEquals(order_by.context, EXPR)
        self.assertEquals(group_by.context, EXPR)

    def test_insert(self):
        expr = Insert({column1: elem1, Func1(): Func2()}, Func2())
        state = State()
        statement = compile(expr, state)
        self.assertTrue(statement in (
                        "INSERT INTO func2() (column1, func1()) "
                        "VALUES (elem1, func2())",
                        "INSERT INTO func2() (func1(), column1) "
                        "VALUES (func2(), elem1)"), statement)
        self.assertEquals(state.parameters, [])

    def test_insert_with_columns(self):
        expr = Insert({Column(column1, table1): elem1,
                       Column(column2, table1): elem2}, table2)
        state = State()
        statement = compile(expr, state)
        self.assertTrue(statement in (
                        'INSERT INTO "table 2" (column1, column2) '
                        'VALUES (elem1, elem2)',
                        'INSERT INTO "table 2" (column2, column1) '
                        'VALUES (elem2, elem1)'), statement)
        self.assertEquals(state.parameters, [])

    def test_insert_with_columns_to_escape(self):
        expr = Insert({Column("column 1", table1): elem1}, table2)
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement,
                          'INSERT INTO "table 2" ("column 1") VALUES (elem1)')
        self.assertEquals(state.parameters, [])

    def test_insert_with_columns_as_raw_strings(self):
        expr = Insert({"column 1": elem1}, table2)
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement,
                          'INSERT INTO "table 2" ("column 1") VALUES (elem1)')
        self.assertEquals(state.parameters, [])

    def test_insert_auto_table(self):
        expr = Insert({Column(column1, table1): elem1})
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, 'INSERT INTO "table 1" (column1) '
                                     'VALUES (elem1)')
        self.assertEquals(state.parameters, [])

    def test_insert_auto_table_default(self):
        expr = Insert({Column(column1): elem1}, default_table=table1)
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, 'INSERT INTO "table 1" (column1) '
                                     'VALUES (elem1)')
        self.assertEquals(state.parameters, [])

    def test_insert_auto_table_unknown(self):
        expr = Insert({Column(column1): elem1})
        self.assertRaises(NoTableError, compile, expr)

    def test_insert_contexts(self):
        column, value, table = track_contexts(3)
        expr = Insert({column: value}, table)
        compile(expr)
        self.assertEquals(column.context, COLUMN_NAME)
        self.assertEquals(value.context, EXPR)
        self.assertEquals(table.context, TABLE)

    def test_insert_bulk(self):
        expr = Insert((Column(column1, table1), Column(column2, table1)),
                      values=[(elem1, elem2), (elem3, elem4)])
        state = State()
        statement = compile(expr, state)
        self.assertEquals(
            statement,
            'INSERT INTO "table 1" (column1, column2) '
            'VALUES (elem1, elem2), (elem3, elem4)')
        self.assertEquals(state.parameters, [])

    def test_insert_select(self):
        expr = Insert((Column(column1, table1), Column(column2, table1)),
                      values=Select(
                        (Column(column3, table3), Column(column4, table4))))
        state = State()
        statement = compile(expr, state)
        self.assertEquals(
            statement,
            'INSERT INTO "table 1" (column1, column2) '
            'SELECT "table 3".column3, "table 4".column4 '
            'FROM "table 3", "table 4"')
        self.assertEquals(state.parameters, [])

    def test_update(self):
        expr = Update({column1: elem1, Func1(): Func2()}, table=Func1())
        state = State()
        statement = compile(expr, state)
        self.assertTrue(statement in (
                        "UPDATE func1() SET column1=elem1, func1()=func2()",
                        "UPDATE func1() SET func1()=func2(), column1=elem1"
                        ), statement)
        self.assertEquals(state.parameters, [])

    def test_update_with_columns(self):
        expr = Update({Column(column1, table1): elem1}, table=table1)
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, 'UPDATE "table 1" SET column1=elem1')
        self.assertEquals(state.parameters, [])

    def test_update_with_columns_to_escape(self):
        expr = Update({Column("column x", table1): elem1}, table=table1)
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, 'UPDATE "table 1" SET "column x"=elem1')
        self.assertEquals(state.parameters, [])

    def test_update_with_columns_as_raw_strings(self):
        expr = Update({"column 1": elem1}, table=table2)
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement,
                          'UPDATE "table 2" SET "column 1"=elem1')
        self.assertEquals(state.parameters, [])

    def test_update_where(self):
        expr = Update({column1: elem1}, Func1(), Func2())
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement,
                          "UPDATE func2() SET column1=elem1 WHERE func1()")
        self.assertEquals(state.parameters, [])

    def test_update_auto_table(self):
        expr = Update({Column(column1, table1): elem1})
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, 'UPDATE "table 1" SET column1=elem1')
        self.assertEquals(state.parameters, [])

    def test_update_auto_table_default(self):
        expr = Update({Column(column1): elem1}, default_table=table1)
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, 'UPDATE "table 1" SET column1=elem1')
        self.assertEquals(state.parameters, [])

    def test_update_auto_table_unknown(self):
        expr = Update({Column(column1): elem1})
        self.assertRaises(CompileError, compile, expr)

    def test_update_with_strings(self):
        expr = Update({column1: elem1}, "1 = 2", table1)
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement,
                          'UPDATE "table 1" SET column1=elem1 WHERE 1 = 2')
        self.assertEquals(state.parameters, [])

    def test_update_contexts(self):
        set_left, set_right, where, table = track_contexts(4)
        expr = Update({set_left: set_right}, where, table)
        compile(expr)
        self.assertEquals(set_left.context, COLUMN_NAME)
        self.assertEquals(set_right.context, COLUMN_NAME)
        self.assertEquals(where.context, EXPR)
        self.assertEquals(table.context, TABLE)

    def test_delete(self):
        expr = Delete(table=table1)
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, 'DELETE FROM "table 1"')
        self.assertEquals(state.parameters, [])

    def test_delete_where(self):
        expr = Delete(Func1(), Func2())
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "DELETE FROM func2() WHERE func1()")
        self.assertEquals(state.parameters, [])

    def test_delete_with_strings(self):
        expr = Delete("1 = 2", table1)
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, 'DELETE FROM "table 1" WHERE 1 = 2')
        self.assertEquals(state.parameters, [])

    def test_delete_auto_table(self):
        expr = Delete(Column(column1, table1) == 1)
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement,
                          'DELETE FROM "table 1" WHERE "table 1".column1 = ?')
        self.assertVariablesEqual(state.parameters, [Variable(1)])

    def test_delete_auto_table_default(self):
        expr = Delete(Column(column1) == 1, default_table=table1)
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement,
                          'DELETE FROM "table 1" WHERE column1 = ?')
        self.assertVariablesEqual(state.parameters, [Variable(1)])

    def test_delete_auto_table_unknown(self):
        expr = Delete(Column(column1) == 1)
        self.assertRaises(NoTableError, compile, expr)

    def test_delete_contexts(self):
        where, table = track_contexts(2)
        expr = Delete(where, table)
        compile(expr)
        self.assertEquals(where.context, EXPR)
        self.assertEquals(table.context, TABLE)

    def test_column(self):
        expr = Column(column1)
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "column1")
        self.assertEquals(state.parameters, [])
        self.assertEquals(expr.compile_cache, "column1")

    def test_column_table(self):
        column = Column(column1, Func1())
        expr = Select(column)
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "SELECT func1().column1 FROM func1()")
        self.assertEquals(state.parameters, [])
        self.assertEquals(column.compile_cache, "column1")

    def test_column_contexts(self):
        table, = track_contexts(1)
        expr = Column(column1, table)
        compile(expr)
        self.assertEquals(table.context, COLUMN_PREFIX)

    def test_column_with_reserved_words(self):
        expr = Select(Column("name 1", "table 1"))
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement,
                          'SELECT "table 1"."name 1" FROM "table 1"')

    def test_row(self):
        expr = Row(column1, column2)
        statement = compile(expr)
        self.assertEquals(statement, "ROW(column1, column2)")

    def test_variable(self):
        expr = Variable("value")
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "?")
        self.assertVariablesEqual(state.parameters, [Variable("value")])

    def test_eq(self):
        expr = Eq(Func1(), Func2())
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "func1() = func2()")
        self.assertEquals(state.parameters, [])

        expr = Func1() == "value"
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "func1() = ?")
        self.assertVariablesEqual(state.parameters, [Variable("value")])

    def test_is_in(self):
        expr = Func1().is_in(["Hello", "World"])
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "func1() IN (?, ?)")
        self.assertVariablesEqual(
            state.parameters, [Variable("Hello"), Variable("World")])

    def test_is_in_empty(self):
        expr = Func1().is_in([])
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "?")
        self.assertVariablesEqual(state.parameters, [BoolVariable(False)])

    def test_is_in_expr(self):
        expr = Func1().is_in(Select(column1))
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "func1() IN (SELECT column1)")
        self.assertEquals(state.parameters, [])

    def test_eq_none(self):
        expr = Func1() == None

        self.assertTrue(expr.expr2 is None)

        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "func1() IS NULL")
        self.assertEquals(state.parameters, [])

    def test_ne(self):
        expr = Ne(Func1(), Func2())
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "func1() != func2()")
        self.assertEquals(state.parameters, [])

        expr = Func1() != "value"
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "func1() != ?")
        self.assertVariablesEqual(state.parameters, [Variable("value")])

    def test_ne_none(self):
        expr = Func1() != None

        self.assertTrue(expr.expr2 is None)

        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "func1() IS NOT NULL")
        self.assertEquals(state.parameters, [])

    def test_gt(self):
        expr = Gt(Func1(), Func2())
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "func1() > func2()")
        self.assertEquals(state.parameters, [])

        expr = Func1() > "value"
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "func1() > ?")
        self.assertVariablesEqual(state.parameters, [Variable("value")])

    def test_ge(self):
        expr = Ge(Func1(), Func2())
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "func1() >= func2()")
        self.assertEquals(state.parameters, [])

        expr = Func1() >= "value"
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "func1() >= ?")
        self.assertVariablesEqual(state.parameters, [Variable("value")])

    def test_lt(self):
        expr = Lt(Func1(), Func2())
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "func1() < func2()")
        self.assertEquals(state.parameters, [])

        expr = Func1() < "value"
        statement = compile(expr, state)
        self.assertEquals(statement, "func1() < ?")
        self.assertVariablesEqual(state.parameters, [Variable("value")])

    def test_le(self):
        expr = Le(Func1(), Func2())
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "func1() <= func2()")
        self.assertEquals(state.parameters, [])

        expr = Func1() <= "value"
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "func1() <= ?")
        self.assertVariablesEqual(state.parameters, [Variable("value")])

    def test_lshift(self):
        expr = LShift(Func1(), Func2())
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "func1()<<func2()")
        self.assertEquals(state.parameters, [])

        expr = Func1() << "value"
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "func1()<<?")
        self.assertVariablesEqual(state.parameters, [Variable("value")])

    def test_rshift(self):
        expr = RShift(Func1(), Func2())
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "func1()>>func2()")
        self.assertEquals(state.parameters, [])

        expr = Func1() >> "value"
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "func1()>>?")
        self.assertVariablesEqual(state.parameters, [Variable("value")])

    def test_like(self):
        expr = Like(Func1(), "value")
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "func1() LIKE ?")
        self.assertVariablesEqual(state.parameters, [RawStrVariable("value")])

        expr = Func1().like("Hello")
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "func1() LIKE ?")
        self.assertVariablesEqual(state.parameters, [Variable("Hello")])

    def test_like_escape(self):
        expr = Like(Func1(), "value", "!")
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "func1() LIKE ? ESCAPE ?")
        self.assertVariablesEqual(state.parameters,
                          [RawStrVariable("value"), RawStrVariable("!")])

        expr = Func1().like("Hello", "!")
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "func1() LIKE ? ESCAPE ?")
        self.assertVariablesEqual(state.parameters,
                          [Variable("Hello"), RawStrVariable("!")])

    def test_like_compareable_case(self):
        expr = Func1().like("Hello")
        self.assertEquals(expr.case_sensitive, None)
        expr = Func1().like("Hello", case_sensitive=True)
        self.assertEquals(expr.case_sensitive, True)
        expr = Func1().like("Hello", case_sensitive=False)
        self.assertEquals(expr.case_sensitive, False)

    def test_in(self):
        expr = In(Func1(), "value")
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "func1() IN (?)")
        self.assertVariablesEqual(state.parameters, [RawStrVariable("value")])

        expr = In(Func1(), elem1)
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "func1() IN (elem1)")
        self.assertEquals(state.parameters, [])

    def test_and(self):
        expr = And(elem1, elem2, And(elem3, elem4))
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "elem1 AND elem2 AND elem3 AND elem4")
        self.assertEquals(state.parameters, [])

        expr = Func1() & "value"
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "func1() AND ?")
        self.assertVariablesEqual(state.parameters, [Variable("value")])

    def test_or(self):
        expr = Or(elem1, elem2, Or(elem3, elem4))
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "elem1 OR elem2 OR elem3 OR elem4")
        self.assertEquals(state.parameters, [])

        expr = Func1() | "value"
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "func1() OR ?")
        self.assertVariablesEqual(state.parameters, [Variable("value")])

    def test_and_with_strings(self):
        expr = And("elem1", "elem2")
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "elem1 AND elem2")
        self.assertEquals(state.parameters, [])

    def test_or_with_strings(self):
        expr = Or("elem1", "elem2")
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "elem1 OR elem2")
        self.assertEquals(state.parameters, [])

    def test_add(self):
        expr = Add(elem1, elem2, Add(elem3, elem4))
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "elem1+elem2+elem3+elem4")
        self.assertEquals(state.parameters, [])

        expr = Func1() + "value"
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "func1()+?")
        self.assertVariablesEqual(state.parameters, [Variable("value")])

    def test_sub(self):
        expr = Sub(elem1, Sub(elem2, elem3))
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "elem1-(elem2-elem3)")
        self.assertEquals(state.parameters, [])

        expr = Sub(Sub(elem1, elem2), elem3)
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "elem1-elem2-elem3")
        self.assertVariablesEqual(state.parameters, [])

        expr = Func1() - "value"
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "func1()-?")
        self.assertVariablesEqual(state.parameters, [Variable("value")])

    def test_mul(self):
        expr = Mul(elem1, elem2, Mul(elem3, elem4))
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "elem1*elem2*elem3*elem4")
        self.assertEquals(state.parameters, [])

        expr = Func1() * "value"
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "func1()*?")
        self.assertVariablesEqual(state.parameters, [Variable("value")])

    def test_div(self):
        expr = Div(elem1, Div(elem2, elem3))
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "elem1/(elem2/elem3)")
        self.assertEquals(state.parameters, [])

        expr = Div(Div(elem1, elem2), elem3)
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "elem1/elem2/elem3")
        self.assertEquals(state.parameters, [])

        expr = Func1() / "value"
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "func1()/?")
        self.assertVariablesEqual(state.parameters, [Variable("value")])

    def test_mod(self):
        expr = Mod(elem1, Mod(elem2, elem3))
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "elem1%(elem2%elem3)")
        self.assertEquals(state.parameters, [])

        expr = Mod(Mod(elem1, elem2), elem3)
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "elem1%elem2%elem3")
        self.assertEquals(state.parameters, [])

        expr = Func1() % "value"
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "func1()%?")
        self.assertVariablesEqual(state.parameters, [Variable("value")])

    def test_func(self):
        expr = Func("myfunc", elem1, Func1(elem2))
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "myfunc(elem1, func1(elem2))")
        self.assertEquals(state.parameters, [])

    def test_named_func(self):
        expr = Func1(elem1, Func2(elem2))
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "func1(elem1, func2(elem2))")
        self.assertEquals(state.parameters, [])

    def test_count(self):
        expr = Count(Func1())
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "COUNT(func1())")
        self.assertEquals(state.parameters, [])

    def test_count_all(self):
        expr = Count()
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "COUNT(*)")
        self.assertEquals(state.parameters, [])

    def test_count_distinct(self):
        expr = Count(Func1(), distinct=True)
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "COUNT(DISTINCT func1())")
        self.assertEquals(state.parameters, [])

    def test_count_distinct_all(self):
        self.assertRaises(ValueError, Count, distinct=True)

    def test_cast(self):
        """
        The L{Cast} expression renders a C{CAST} function call with a
        user-defined input value and the type to cast it to.
        """
        expr = Cast(Func1(), "TEXT")
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "CAST(func1() AS TEXT)")
        self.assertEquals(state.parameters, [])

    def test_max(self):
        expr = Max(Func1())
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "MAX(func1())")
        self.assertEquals(state.parameters, [])

    def test_min(self):
        expr = Min(Func1())
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "MIN(func1())")
        self.assertEquals(state.parameters, [])

    def test_avg(self):
        expr = Avg(Func1())
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "AVG(func1())")
        self.assertEquals(state.parameters, [])

    def test_sum(self):
        expr = Sum(Func1())
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "SUM(func1())")
        self.assertEquals(state.parameters, [])

    def test_lower(self):
        expr = Lower(Func1())
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "LOWER(func1())")
        self.assertEquals(state.parameters, [])

        expr = Func1().lower()
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "LOWER(func1())")
        self.assertEquals(state.parameters, [])

    def test_upper(self):
        expr = Upper(Func1())
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "UPPER(func1())")
        self.assertEquals(state.parameters, [])

        expr = Func1().upper()
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "UPPER(func1())")
        self.assertEquals(state.parameters, [])

    def test_coalesce(self):
        expr = Coalesce(Func1())
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "COALESCE(func1())")
        self.assertEquals(state.parameters, [])

    def test_coalesce_with_many_arguments(self):
        expr = Coalesce(Func1(), Func2(), None)
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "COALESCE(func1(), func2(), NULL)")
        self.assertEquals(state.parameters, [])

    def test_not(self):
        expr = Not(Func1())
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "NOT func1()")
        self.assertEquals(state.parameters, [])

    def test_exists(self):
        expr = Exists(Func1())
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "EXISTS func1()")
        self.assertEquals(state.parameters, [])

    def test_neg(self):
        expr = Neg(Func1())
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "- func1()")
        self.assertEquals(state.parameters, [])

        expr = -Func1()
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "- func1()")
        self.assertEquals(state.parameters, [])

    def test_asc(self):
        expr = Asc(Func1())
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "func1() ASC")
        self.assertEquals(state.parameters, [])

    def test_desc(self):
        expr = Desc(Func1())
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "func1() DESC")
        self.assertEquals(state.parameters, [])

    def test_asc_with_string(self):
        expr = Asc("column")
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "column ASC")
        self.assertEquals(state.parameters, [])

    def test_desc_with_string(self):
        expr = Desc("column")
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "column DESC")
        self.assertEquals(state.parameters, [])

    def test_sql(self):
        expr = SQL("expression")
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "expression")
        self.assertEquals(state.parameters, [])

    def test_sql_params(self):
        expr = SQL("expression", ["params"])
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "expression")
        self.assertEquals(state.parameters, ["params"])

    def test_sql_invalid_params(self):
        expr = SQL("expression", "not a list or tuple")
        self.assertRaises(CompileError, compile, expr)

    def test_sql_tables(self):
        expr = Select([column1, Func1()], SQL("expression", [], Func2()))
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement,
                          "SELECT column1, func1() FROM func2() "
                          "WHERE expression")
        self.assertEquals(state.parameters, [])

    def test_sql_tables_with_list_or_tuple(self):
        sql = SQL("expression", [], [Func1(), Func2()])
        expr = Select(column1, sql)
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement,
                          "SELECT column1 FROM func1(), func2() "
                          "WHERE expression")
        self.assertEquals(state.parameters, [])

        sql = SQL("expression", [], (Func1(), Func2()))
        expr = Select(column1, sql)
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement,
                          "SELECT column1 FROM func1(), func2() "
                          "WHERE expression")
        self.assertEquals(state.parameters, [])

    def test_sql_comparison(self):
        expr = SQL("expression1") & SQL("expression2")
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "(expression1) AND (expression2)")
        self.assertEquals(state.parameters, [])

    def test_table(self):
        expr = Table(table1)
        self.assertIdentical(expr.compile_cache, None)
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, '"table 1"')
        self.assertEquals(state.parameters, [])
        self.assertEquals(expr.compile_cache, '"table 1"')

    def test_alias(self):
        expr = Alias(Table(table1), "name")
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "name")
        self.assertEquals(state.parameters, [])

    def test_alias_in_tables(self):
        expr = Select(column1, tables=Alias(Table(table1), "alias 1"))
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement,
                          'SELECT column1 FROM "table 1" AS "alias 1"')
        self.assertEquals(state.parameters, [])

    def test_alias_in_tables_auto_name(self):
        expr = Select(column1, tables=Alias(Table(table1)))
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement[:statement.rfind("_")+1],
                          'SELECT column1 FROM "table 1" AS "_')
        self.assertEquals(state.parameters, [])

    def test_alias_in_column_prefix(self):
        expr = Select(Column(column1, Alias(Table(table1), "alias 1")))
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, 'SELECT "alias 1".column1 '
                                     'FROM "table 1" AS "alias 1"')
        self.assertEquals(state.parameters, [])

    def test_alias_for_column(self):
        expr = Select(Alias(Column(column1, table1), "alias 1"))
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, 'SELECT "table 1".column1 AS "alias 1" '
                                     'FROM "table 1"')
        self.assertEquals(state.parameters, [])

    def test_alias_union(self):
        union = Union(Select(elem1), Select(elem2))
        expr = Select(elem3, tables=Alias(union, "alias"))
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement,
                          "SELECT elem3 FROM "
                          "((SELECT elem1) UNION (SELECT elem2)) AS alias")
        self.assertEquals(state.parameters, [])

    def test_distinct(self):
        """L{Distinct} adds a DISTINCT prefix to the given expression."""
        distinct = Distinct(Column(elem1))
        state = State()
        statement = compile(distinct, state)
        self.assertEquals(statement, "DISTINCT elem1")
        self.assertEquals(state.parameters, [])

    def test_join(self):
        expr = Join(Func1())
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "JOIN func1()")
        self.assertEquals(state.parameters, [])

    def test_join_on(self):
        expr = Join(Func1(), Func2() == "value")
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "JOIN func1() ON func2() = ?")
        self.assertVariablesEqual(state.parameters, [Variable("value")])

    def test_join_on_with_string(self):
        expr = Join(Func1(), on="a = b")
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "JOIN func1() ON a = b")
        self.assertEquals(state.parameters, [])

    def test_join_left_right(self):
        expr = Join(table1, table2)
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, '"table 1" JOIN "table 2"')
        self.assertEquals(state.parameters, [])

    def test_join_nested(self):
        expr = Join(table1, Join(table2, table3))
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, '"table 1" JOIN '
                                     '("table 2" JOIN "table 3")')
        self.assertEquals(state.parameters, [])

    def test_join_double_nested(self):
        expr = Join(Join(table1, table2), Join(table3, table4))
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, '"table 1" JOIN "table 2" JOIN '
                                     '("table 3" JOIN "table 4")')
        self.assertEquals(state.parameters, [])

    def test_join_table(self):
        expr = Join(Table(table1), Table(table2))
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, '"table 1" JOIN "table 2"')
        self.assertEquals(state.parameters, [])

    def test_join_contexts(self):
        table1, table2, on = track_contexts(3)
        expr = Join(table1, table2, on)
        compile(expr)
        self.assertEquals(table1.context, None)
        self.assertEquals(table2.context, None)
        self.assertEquals(on.context, EXPR)

    def test_left_join(self):
        expr = LeftJoin(Func1())
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "LEFT JOIN func1()")
        self.assertEquals(state.parameters, [])

    def test_left_join_on(self):
        expr = LeftJoin(Func1(), Func2() == "value")
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "LEFT JOIN func1() ON func2() = ?")
        self.assertVariablesEqual(state.parameters, [Variable("value")])

    def test_right_join(self):
        expr = RightJoin(Func1())
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "RIGHT JOIN func1()")
        self.assertEquals(state.parameters, [])

    def test_right_join_on(self):
        expr = RightJoin(Func1(), Func2() == "value")
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "RIGHT JOIN func1() ON func2() = ?")
        self.assertVariablesEqual(state.parameters, [Variable("value")])

    def test_natural_join(self):
        expr = NaturalJoin(Func1())
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "NATURAL JOIN func1()")
        self.assertEquals(state.parameters, [])

    def test_natural_join_on(self):
        expr = NaturalJoin(Func1(), Func2() == "value")
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "NATURAL JOIN func1() ON func2() = ?")
        self.assertVariablesEqual(state.parameters, [Variable("value")])

    def test_natural_left_join(self):
        expr = NaturalLeftJoin(Func1())
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "NATURAL LEFT JOIN func1()")
        self.assertEquals(state.parameters, [])

    def test_natural_left_join_on(self):
        expr = NaturalLeftJoin(Func1(), Func2() == "value")
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "NATURAL LEFT JOIN func1() "
                                     "ON func2() = ?")
        self.assertVariablesEqual(state.parameters, [Variable("value")])

    def test_natural_right_join(self):
        expr = NaturalRightJoin(Func1())
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "NATURAL RIGHT JOIN func1()")
        self.assertEquals(state.parameters, [])

    def test_natural_right_join_on(self):
        expr = NaturalRightJoin(Func1(), Func2() == "value")
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "NATURAL RIGHT JOIN func1() "
                                     "ON func2() = ?")
        self.assertVariablesEqual(state.parameters, [Variable("value")])

    def test_union(self):
        expr = Union(Func1(), elem2, elem3)
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "func1() UNION elem2 UNION elem3")
        self.assertEquals(state.parameters, [])

    def test_union_all(self):
        expr = Union(Func1(), elem2, elem3, all=True)
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "func1() UNION ALL elem2 UNION ALL elem3")
        self.assertEquals(state.parameters, [])

    def test_union_order_by_limit_offset(self):
        expr = Union(elem1, elem2, order_by=Func1(), limit=1, offset=2)
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "elem1 UNION elem2 ORDER BY func1() "
                                     "LIMIT 1 OFFSET 2")
        self.assertEquals(state.parameters, [])

    def test_union_select(self):
        expr = Union(Select(elem1), Select(elem2))
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "(SELECT elem1) UNION (SELECT elem2)")
        self.assertEquals(state.parameters, [])

    def test_union_select_nested(self):
        expr = Union(Select(elem1), Union(Select(elem2), Select(elem3)))
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "(SELECT elem1) UNION"
                                     " ((SELECT elem2) UNION (SELECT elem3))")
        self.assertEquals(state.parameters, [])

    def test_union_order_by_and_select(self):
        """
        When ORDER BY is present, databases usually have trouble using
        fully qualified column names.  Because of that, we transform
        pure column names into aliases, and use them in the ORDER BY.
        """
        Alias.auto_counter = 0
        column1 = Column(elem1)
        column2 = Column(elem2)
        expr = Union(Select(column1), Select(column2),
                     order_by=(column1, column2))
        state = State()
        statement = compile(expr, state)
        self.assertEquals(
            statement,
            '(SELECT elem1 AS "_1") UNION (SELECT elem2 AS "_2") '
            'ORDER BY "_1", "_2"')
        self.assertEquals(state.parameters, [])

    def test_union_contexts(self):
        select1, select2, order_by = track_contexts(3)
        expr = Union(select1, select2, order_by=order_by)
        compile(expr)
        self.assertEquals(select1.context, SELECT)
        self.assertEquals(select2.context, SELECT)
        self.assertEquals(order_by.context, COLUMN_NAME)

    def test_except(self):
        expr = Except(Func1(), elem2, elem3)
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "func1() EXCEPT elem2 EXCEPT elem3")
        self.assertEquals(state.parameters, [])

    def test_except_all(self):
        expr = Except(Func1(), elem2, elem3, all=True)
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "func1() EXCEPT ALL elem2 "
                                     "EXCEPT ALL elem3")
        self.assertEquals(state.parameters, [])

    def test_except_order_by_limit_offset(self):
        expr = Except(elem1, elem2, order_by=Func1(), limit=1, offset=2)
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "elem1 EXCEPT elem2 ORDER BY func1() "
                                     "LIMIT 1 OFFSET 2")
        self.assertEquals(state.parameters, [])

    def test_except_select(self):
        expr = Except(Select(elem1), Select(elem2))
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "(SELECT elem1) EXCEPT (SELECT elem2)")
        self.assertEquals(state.parameters, [])

    def test_except_select_nested(self):
        expr = Except(Select(elem1), Except(Select(elem2), Select(elem3)))
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "(SELECT elem1) EXCEPT"
                                     " ((SELECT elem2) EXCEPT (SELECT elem3))")
        self.assertEquals(state.parameters, [])

    def test_except_contexts(self):
        select1, select2, order_by = track_contexts(3)
        expr = Except(select1, select2, order_by=order_by)
        compile(expr)
        self.assertEquals(select1.context, SELECT)
        self.assertEquals(select2.context, SELECT)
        self.assertEquals(order_by.context, COLUMN_NAME)

    def test_intersect(self):
        expr = Intersect(Func1(), elem2, elem3)
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "func1() INTERSECT elem2 INTERSECT elem3")
        self.assertEquals(state.parameters, [])

    def test_intersect_all(self):
        expr = Intersect(Func1(), elem2, elem3, all=True)
        state = State()
        statement = compile(expr, state)
        self.assertEquals(
            statement, "func1() INTERSECT ALL elem2 INTERSECT ALL elem3")
        self.assertEquals(state.parameters, [])

    def test_intersect_order_by_limit_offset(self):
        expr = Intersect(elem1, elem2, order_by=Func1(), limit=1, offset=2)
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "elem1 INTERSECT elem2 ORDER BY func1() "
                                     "LIMIT 1 OFFSET 2")
        self.assertEquals(state.parameters, [])

    def test_intersect_select(self):
        expr = Intersect(Select(elem1), Select(elem2))
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "(SELECT elem1) INTERSECT (SELECT elem2)")
        self.assertEquals(state.parameters, [])

    def test_intersect_select_nested(self):
        expr = Intersect(
            Select(elem1), Intersect(Select(elem2), Select(elem3)))
        state = State()
        statement = compile(expr, state)
        self.assertEquals(
            statement, "(SELECT elem1) INTERSECT"
                       " ((SELECT elem2) INTERSECT (SELECT elem3))")
        self.assertEquals(state.parameters, [])

    def test_intersect_contexts(self):
        select1, select2, order_by = track_contexts(3)
        expr = Intersect(select1, select2, order_by=order_by)
        compile(expr)
        self.assertEquals(select1.context, SELECT)
        self.assertEquals(select2.context, SELECT)
        self.assertEquals(order_by.context, COLUMN_NAME)

    def test_auto_table(self):
        expr = Select(AutoTables(1, [table1]))
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, 'SELECT ? FROM "table 1"')
        self.assertVariablesEqual(state.parameters, [IntVariable(1)])

    def test_auto_tables_with_column(self):
        expr = Select(AutoTables(Column(elem1, table1), [table2]))
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, 'SELECT "table 1".elem1 '
                                     'FROM "table 1", "table 2"')
        self.assertEquals(state.parameters, [])

    def test_auto_tables_with_column_and_replace(self):
        expr = Select(AutoTables(Column(elem1, table1), [table2], replace=True))
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, 'SELECT "table 1".elem1 FROM "table 2"')
        self.assertEquals(state.parameters, [])

    def test_auto_tables_with_join(self):
        expr = Select(AutoTables(Column(elem1, table1), [LeftJoin(table2)]))
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, 'SELECT "table 1".elem1 FROM "table 1" '
                                     'LEFT JOIN "table 2"')
        self.assertEquals(state.parameters, [])

    def test_auto_tables_with_join_with_left_table(self):
        expr = Select(AutoTables(Column(elem1, table1),
                                 [LeftJoin(table1, table2)]))
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, 'SELECT "table 1".elem1 FROM "table 1" '
                                     'LEFT JOIN "table 2"')
        self.assertEquals(state.parameters, [])

    def test_auto_tables_duplicated(self):
        expr = Select([AutoTables(Column(elem1, table1), [Join(table2)]),
                       AutoTables(Column(elem2, table2), [Join(table1)]),
                       AutoTables(Column(elem3, table1), [Join(table1)]),
                       AutoTables(Column(elem4, table3), [table1]),
                       AutoTables(Column(elem5, table1),
                                  [Join(table4, table5)])])
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement,
                          'SELECT "table 1".elem1, "table 2".elem2, '
                          '"table 1".elem3, "table 3".elem4, "table 1".elem5 '
                          'FROM "table 3", "table 4" JOIN "table 5" JOIN '
                          '"table 1" JOIN "table 2"')
        self.assertEquals(state.parameters, [])

    def test_auto_tables_duplicated_nested(self):
        expr = Select(AutoTables(Column(elem1, table1), [Join(table2)]),
                      In(1, Select(AutoTables(Column(elem1, table1),
                                              [Join(table2)]))))
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement,
                          'SELECT "table 1".elem1 FROM "table 1" JOIN '
                          '"table 2" WHERE ? IN (SELECT "table 1".elem1 '
                          'FROM "table 1" JOIN "table 2")')
        self.assertVariablesEqual(state.parameters, [IntVariable(1)])

    def test_sql_token(self):
        expr = SQLToken("something")
        state = State()
        statement = compile(expr, state)
        self.assertEquals(statement, "something")
        self.assertEquals(state.parameters, [])

    def test_sql_token_spaces(self):
        expr = SQLToken("some thing")
        statement = compile(expr)
        self.assertEquals(statement, '"some thing"')

    def test_sql_token_quotes(self):
        expr = SQLToken("some'thing")
        statement = compile(expr)
        self.assertEquals(statement, '"some\'thing"')

    def test_sql_token_double_quotes(self):
        expr = SQLToken('some"thing')
        statement = compile(expr)
        self.assertEquals(statement, '"some""thing"')

    def test_sql_token_reserved(self):
        custom_compile = compile.create_child()
        custom_compile.add_reserved_words(["something"])
        expr = SQLToken("something")
        state = State()
        statement = custom_compile(expr, state)
        self.assertEquals(statement, '"something"')
        self.assertEquals(state.parameters, [])

    def test_sql_token_reserved_from_parent(self):
        expr = SQLToken("something")
        parent_compile = compile.create_child()
        child_compile = parent_compile.create_child()
        statement = child_compile(expr)
        self.assertEquals(statement, "something")
        parent_compile.add_reserved_words(["something"])
        statement = child_compile(expr)
        self.assertEquals(statement, '"something"')

    def test_sql_token_remove_reserved_word_on_child(self):
        expr = SQLToken("something")
        parent_compile = compile.create_child()
        parent_compile.add_reserved_words(["something"])
        child_compile = parent_compile.create_child()
        statement = child_compile(expr)
        self.assertEquals(statement, '"something"')
        child_compile.remove_reserved_words(["something"])
        statement = child_compile(expr)
        self.assertEquals(statement, "something")

    def test_is_reserved_word(self):
        parent_compile = compile.create_child()
        child_compile = parent_compile.create_child()
        self.assertEquals(child_compile.is_reserved_word("someTHING"), False)
        parent_compile.add_reserved_words(["SOMEthing"])
        self.assertEquals(child_compile.is_reserved_word("somETHing"), True)
        child_compile.remove_reserved_words(["soMETHing"])
        self.assertEquals(child_compile.is_reserved_word("somethING"), False)

    def test_sql1992_reserved_words(self):
        reserved_words = """
            absolute action add all allocate alter and any are as asc assertion
            at authorization avg begin between bit bit_length both by cascade
            cascaded case cast catalog char character char_ length
            character_length check close coalesce collate collation column
            commit connect connection constraint constraints continue convert
            corresponding count create cross current current_date current_time
            current_timestamp current_ user cursor date day deallocate dec
            decimal declare default deferrable deferred delete desc describe
            descriptor diagnostics disconnect distinct domain double drop else
            end end-exec escape except exception exec execute exists external
            extract false fetch first float for foreign found from full get
            global go goto grant group having hour identity immediate in
            indicator initially inner input insensitive insert int integer
            intersect interval into is isolation join key language last leading
            left level like local lower match max min minute module month names
            national natural nchar next no not null nullif numeric octet_length
            of on only open option or order outer output overlaps pad partial
            position precision prepare preserve primary prior privileges
            procedure public read real references relative restrict revoke
            right rollback rows schema scroll second section select session
            session_ user set size smallint some space sql sqlcode sqlerror
            sqlstate substring sum system_user table temporary then time
            timestamp timezone_ hour timezone_minute to trailing transaction
            translate translation trim true union unique unknown update upper
            usage user using value values varchar varying view when whenever
            where with work write year zone
            """.split()
        for word in reserved_words:
            self.assertEquals(compile.is_reserved_word(word), True)


class CompilePythonTest(TestHelper):

    def test_precedence(self):
        for i in range(10):
            exec "e%d = SQLRaw('%d')" % (i, i)
        expr = And(e1, Or(e2, e3),
                   Add(e4, Mul(e5, Sub(e6, Div(e7, Div(e8, e9))))))
        py_expr = compile_python(expr)
        self.assertEquals(py_expr, "1 and (2 or 3) and 4+5*(6-7/(8/9))")

    def test_get_precedence(self):
        self.assertTrue(compile_python.get_precedence(Or) <
                        compile_python.get_precedence(And))
        self.assertTrue(compile_python.get_precedence(Add) <
                        compile_python.get_precedence(Mul))
        self.assertTrue(compile_python.get_precedence(Sub) <
                        compile_python.get_precedence(Div))

    def test_compile_sequence(self):
        expr = [elem1, Variable(1), (Variable(2), None)]
        state = State()
        py_expr = compile_python(expr, state)
        self.assertEquals(py_expr, "elem1, _0, _1, None")
        self.assertEquals(state.parameters, [1, 2])

    def test_compile_invalid(self):
        self.assertRaises(CompileError, compile_python, object())
        self.assertRaises(CompileError, compile_python, [object()])

    def test_compile_unsupported(self):
        self.assertRaises(CompileError, compile_python, Expr())
        self.assertRaises(CompileError, compile_python, Func1())

    def test_str(self):
        py_expr = compile_python("str")
        self.assertEquals(py_expr, "'str'")

    def test_unicode(self):
        py_expr = compile_python(u"str")
        self.assertEquals(py_expr, "u'str'")

    def test_int(self):
        py_expr = compile_python(1)
        self.assertEquals(py_expr, "1")

    def test_long(self):
        py_expr = compile_python(1L)
        self.assertEquals(py_expr, "1L")

    def test_bool(self):
        state = State()
        py_expr = compile_python(True, state)
        self.assertEquals(py_expr, "_0")
        self.assertEquals(state.parameters, [True])

    def test_float(self):
        py_expr = compile_python(1.1)
        self.assertEquals(py_expr, repr(1.1))

    def test_datetime(self):
        dt = datetime(1977, 5, 4, 12, 34)
        state = State()
        py_expr = compile_python(dt, state)
        self.assertEquals(py_expr, "_0")
        self.assertEquals(state.parameters, [dt])

    def test_date(self):
        d = date(1977, 5, 4)
        state = State()
        py_expr = compile_python(d, state)
        self.assertEquals(py_expr, "_0")
        self.assertEquals(state.parameters, [d])

    def test_time(self):
        t = time(12, 34)
        state = State()
        py_expr = compile_python(t, state)
        self.assertEquals(py_expr, "_0")
        self.assertEquals(state.parameters, [t])

    def test_timedelta(self):
        td = timedelta(days=1, seconds=2, microseconds=3)
        state = State()
        py_expr = compile_python(td, state)
        self.assertEquals(py_expr, "_0")
        self.assertEquals(state.parameters, [td])

    def test_none(self):
        py_expr = compile_python(None)
        self.assertEquals(py_expr, "None")

    def test_column(self):
        expr = Column(column1)
        state = State()
        py_expr = compile_python(expr, state)
        self.assertEquals(py_expr, "get_column(_0)")
        self.assertEquals(state.parameters, [expr])

    def test_column_table(self):
        expr = Column(column1, table1)
        state = State()
        py_expr = compile_python(expr, state)
        self.assertEquals(py_expr, "get_column(_0)")
        self.assertEquals(state.parameters, [expr])

    def test_variable(self):
        expr = Variable("value")
        state = State()
        py_expr = compile_python(expr, state)
        self.assertEquals(py_expr, "_0")
        self.assertEquals(state.parameters, ["value"])

    def test_eq(self):
        expr = Eq(Variable(1), Variable(2))
        state = State()
        py_expr = compile_python(expr, state)
        self.assertEquals(py_expr, "_0 == _1")
        self.assertEquals(state.parameters, [1, 2])

    def test_ne(self):
        expr = Ne(Variable(1), Variable(2))
        state = State()
        py_expr = compile_python(expr, state)
        self.assertEquals(py_expr, "_0 != _1")
        self.assertEquals(state.parameters, [1, 2])

    def test_gt(self):
        expr = Gt(Variable(1), Variable(2))
        state = State()
        py_expr = compile_python(expr, state)
        self.assertEquals(py_expr, "_0 > _1")
        self.assertEquals(state.parameters, [1, 2])

    def test_ge(self):
        expr = Ge(Variable(1), Variable(2))
        state = State()
        py_expr = compile_python(expr, state)
        self.assertEquals(py_expr, "_0 >= _1")
        self.assertEquals(state.parameters, [1, 2])

    def test_lt(self):
        expr = Lt(Variable(1), Variable(2))
        state = State()
        py_expr = compile_python(expr, state)
        self.assertEquals(py_expr, "_0 < _1")
        self.assertEquals(state.parameters, [1, 2])

    def test_le(self):
        expr = Le(Variable(1), Variable(2))
        state = State()
        py_expr = compile_python(expr, state)
        self.assertEquals(py_expr, "_0 <= _1")
        self.assertEquals(state.parameters, [1, 2])

    def test_lshift(self):
        expr = LShift(Variable(1), Variable(2))
        state = State()
        py_expr = compile_python(expr, state)
        self.assertEquals(py_expr, "_0<<_1")
        self.assertEquals(state.parameters, [1, 2])

    def test_rshift(self):
        expr = RShift(Variable(1), Variable(2))
        state = State()
        py_expr = compile_python(expr, state)
        self.assertEquals(py_expr, "_0>>_1")
        self.assertEquals(state.parameters, [1, 2])

    def test_in(self):
        expr = In(Variable(1), Variable(2))
        state = State()
        py_expr = compile_python(expr, state)
        self.assertEquals(py_expr, "_0 in (_1,)")
        self.assertEquals(state.parameters, [1, 2])

    def test_and(self):
        expr = And(elem1, elem2, And(elem3, elem4))
        py_expr = compile_python(expr)
        self.assertEquals(py_expr, "elem1 and elem2 and elem3 and elem4")

    def test_or(self):
        expr = Or(elem1, elem2, Or(elem3, elem4))
        py_expr = compile_python(expr)
        self.assertEquals(py_expr, "elem1 or elem2 or elem3 or elem4")

    def test_add(self):
        expr = Add(elem1, elem2, Add(elem3, elem4))
        py_expr = compile_python(expr)
        self.assertEquals(py_expr, "elem1+elem2+elem3+elem4")

    def test_neg(self):
        expr = Neg(elem1)
        py_expr = compile_python(expr)
        self.assertEquals(py_expr, "-elem1")

    def test_sub(self):
        expr = Sub(elem1, Sub(elem2, elem3))
        py_expr = compile_python(expr)
        self.assertEquals(py_expr, "elem1-(elem2-elem3)")

        expr = Sub(Sub(elem1, elem2), elem3)
        py_expr = compile_python(expr)
        self.assertEquals(py_expr, "elem1-elem2-elem3")

    def test_mul(self):
        expr = Mul(elem1, elem2, Mul(elem3, elem4))
        py_expr = compile_python(expr)
        self.assertEquals(py_expr, "elem1*elem2*elem3*elem4")

    def test_div(self):
        expr = Div(elem1, Div(elem2, elem3))
        py_expr = compile_python(expr)
        self.assertEquals(py_expr, "elem1/(elem2/elem3)")

        expr = Div(Div(elem1, elem2), elem3)
        py_expr = compile_python(expr)
        self.assertEquals(py_expr, "elem1/elem2/elem3")

    def test_mod(self):
        expr = Mod(elem1, Mod(elem2, elem3))
        py_expr = compile_python(expr)
        self.assertEquals(py_expr, "elem1%(elem2%elem3)")

        expr = Mod(Mod(elem1, elem2), elem3)
        py_expr = compile_python(expr)
        self.assertEquals(py_expr, "elem1%elem2%elem3")

    def test_match(self):
        col1 = Column(column1)
        col2 = Column(column2)

        match = compile_python.get_matcher((col1 > 10) & (col2 < 10))

        self.assertTrue(match({col1: 15, col2: 5}.get))
        self.assertFalse(match({col1: 5, col2: 15}.get))

    def test_match_bad_repr(self):
        """The get_matcher() works for expressions containing values
        whose repr is not valid Python syntax."""
        class BadRepr(object):
            def __repr__(self):
                return "$Not a valid Python expression$"

        value = BadRepr()
        col1 = Column(column1)
        match = compile_python.get_matcher(col1 == Variable(value))
        self.assertTrue(match({col1: value}.get))


class LazyValueExprTest(TestHelper):

    def test_expr_is_lazy_value(self):
        marker = object()
        expr = SQL("Hullah!")
        variable = Variable()
        variable.set(expr)
        self.assertTrue(variable.get(marker) is marker)
