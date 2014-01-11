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
import os

from storm.databases.mysql import MySQL
from storm.database import create_database
from storm.expr import Column, Insert
from storm.uri import URI
from storm.variables import IntVariable, UnicodeVariable

from tests.databases.base import (
    DatabaseTest, DatabaseDisconnectionTest, UnsupportedDatabaseTest)
from tests.helper import TestHelper


class MySQLTest(DatabaseTest, TestHelper):

    supports_microseconds = False

    def is_supported(self):
        return bool(os.environ.get("STORM_MYSQL_URI"))

    def create_database(self):
        self.database = create_database(os.environ["STORM_MYSQL_URI"])

    def create_tables(self):
        self.connection.execute("CREATE TABLE number "
                                "(one INTEGER, two INTEGER, three INTEGER)")
        self.connection.execute("CREATE TABLE test "
                                "(id INT AUTO_INCREMENT PRIMARY KEY,"
                                " title VARCHAR(50)) ENGINE=InnoDB")
        self.connection.execute("CREATE TABLE datetime_test "
                                "(id INT AUTO_INCREMENT PRIMARY KEY,"
                                " dt TIMESTAMP, d DATE, t TIME, td TEXT) "
                                "ENGINE=InnoDB")
        self.connection.execute("CREATE TABLE bin_test "
                                "(id INT AUTO_INCREMENT PRIMARY KEY,"
                                " b BLOB) ENGINE=InnoDB")

    def test_wb_create_database(self):
        database = create_database("mysql://un:pw@ht:12/db?unix_socket=us")
        self.assertTrue(isinstance(database, MySQL))
        for key, value in [("db", "db"), ("host", "ht"), ("port", 12),
                           ("user", "un"), ("passwd", "pw"),
                           ("unix_socket", "us")]:
            self.assertEquals(database._connect_kwargs.get(key), value)

    def test_charset_defaults_to_utf8(self):
        result = self.connection.execute("SELECT @@character_set_client")
        self.assertEquals(result.get_one(), ("utf8",))

    def test_charset_option(self):
        uri = URI(os.environ["STORM_MYSQL_URI"])
        uri.options["charset"] = "ascii"
        database = create_database(uri)
        connection = database.connect()
        result = connection.execute("SELECT @@character_set_client")
        self.assertEquals(result.get_one(), ("ascii",))

    def test_get_insert_identity(self):
        # Primary keys are filled in during execute() for MySQL
        pass

    def test_get_insert_identity_composed(self):
        # Primary keys are filled in during execute() for MySQL
        pass

    def test_execute_insert_auto_increment_primary_key(self):
        id_column = Column("id", "test")
        id_variable = IntVariable()
        title_column = Column("title", "test")
        title_variable = UnicodeVariable(u"testing")

        # This is not part of the table.  It is just used to show that
        # only one primary key variable is set from the insert ID.
        dummy_column = Column("dummy", "test")
        dummy_variable = IntVariable()

        insert = Insert({title_column: title_variable},
                        primary_columns=(id_column, dummy_column),
                        primary_variables=(id_variable, dummy_variable))
        self.connection.execute(insert)
        self.assertTrue(id_variable.is_defined())
        self.assertFalse(dummy_variable.is_defined())

        # The newly inserted row should have the maximum id value for
        # the table.
        result = self.connection.execute("SELECT MAX(id) FROM test")
        self.assertEqual(result.get_one()[0], id_variable.get())

    def test_mysql_specific_reserved_words(self):
        reserved_words = """
            accessible analyze asensitive before bigint binary blob call
            change condition current_user database databases day_hour
            day_microsecond day_minute day_second delayed deterministic
            distinctrow div dual each elseif enclosed escaped exit explain
            float4 float8 force fulltext high_priority hour_microsecond
            hour_minute hour_second if ignore index infile inout int1 int2
            int3 int4 int8 iterate keys kill leave limit linear lines load
            localtime localtimestamp lock long longblob longtext loop
            low_priority master_ssl_verify_server_cert mediumblob mediumint
            mediumtext middleint minute_microsecond minute_second mod modifies
            no_write_to_binlog optimize optionally out outfile purge range
            read_write reads regexp release rename repeat replace require
            return rlike schemas second_microsecond sensitive separator show
            spatial specific sql_big_result sql_calc_found_rows
            sql_small_result sqlexception sqlwarning ssl starting
            straight_join terminated tinyblob tinyint tinytext trigger undo
            unlock unsigned use utc_date utc_time utc_timestamp varbinary
            varcharacter while xor year_month zerofill
            """.split()
        for word in reserved_words:
            self.assertTrue(self.connection.compile.is_reserved_word(word),
                            "Word missing: %s" % (word,))


class MySQLUnsupportedTest(UnsupportedDatabaseTest, TestHelper):

    dbapi_module_names = ["MySQLdb"]
    db_module_name = "mysql"


class MySQLDisconnectionTest(DatabaseDisconnectionTest, TestHelper):

    environment_variable = "STORM_MYSQL_URI"
    host_environment_variable = "STORM_MYSQL_HOST_URI"
    default_port = 3306
