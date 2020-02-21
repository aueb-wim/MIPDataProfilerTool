from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import pytest
from mipqctool.qccolumn import QcColumn
from mipqctool.config import ERROR


MISSING_VALUES = ['']
DATE_DESC = {'name': 'testvar',
             'format': '%d/%m/%Y',
             'type': 'date',
             'MIPType': 'date',
             'constraints': {
                    'minimum': '1/1/1900',
                    }
             }
NOMINAL_DESC = {'name': 'testvar',
                'format': 'default',
                'type': 'string',
                'MIPType': 'nominal',
                'constraints': {
                    'enum': ['Category1', 'Category2', 'Another3']
                }}
NUMERICAL_DESC = {'name': 'testvar',
                  'format': 'default',
                  'type': 'number',
                  'MIPType': 'numerical',
                  'constraints': {
                      'minimum': 0,
                      'maximum': 10
                      }
                  }
INTEGER_DESC = {'name': 'testvar',
                'format': 'default',
                'type': 'integer',
                'MIPType': 'integer',
                'constraints': {
                    'minimum': 3,
                    'maximum': 5
                    }
                }

INTEGER_VALUES = ['1', '3', '3', '2', '5', '4', '2.5', '',
                  'not_int', '20191212', '5.6']
NUMERICAL_VALUES = ['-0.12', '2.31', 'not_num', '21/12/2019',
                    '4', '3.2', '', '']
DATE_VALUES = ['1/12/2019', '1-21-2013', '15 Aug 2012', '20011212', '',
               '31', 'not_date', '1/1/1880']
NOMINAL_VALUES = ['cAtegory1', 'not_value', 'Category1', 'Category2',
                  'another1', '', '', 'Category2', 'CATEGORY2']


@pytest.mark.parametrize('descriptor, values, result', [
    (INTEGER_DESC, INTEGER_VALUES,
     [(1, '3'), (2, '3'), (4, '5'), (5, '4'), (7, '')]),
    (NUMERICAL_DESC, NUMERICAL_VALUES,
     [(1, '2.31'), (4, '4'), (5, '3.2'), (6, ''), (7, '')]),
    (DATE_DESC, DATE_VALUES, [(0, '1/12/2019'), (4, '')]),
    (NOMINAL_DESC, NOMINAL_VALUES,
     [(2, 'Category1'), (3, 'Category2'), (5, ''), (6, ''),
      (7, 'Category2')])
])
def test_validate_valid(descriptor, values, result):
    testcolumn = QcColumn(values, descriptor)
    testcolumn.validate()
    with pytest.warns(None) as recorded:
        assert testcolumn._QcColumn__validated_pairs == result
        assert recorded.list == []


@pytest.mark.parametrize('descriptor, values, result', [
    (INTEGER_DESC, INTEGER_VALUES, [(6, '2.5'), (8, 'not_int'), (10, '5.6')]),
    (NUMERICAL_DESC, NUMERICAL_VALUES,
     [(2, 'not_num'), (3, '21/12/2019')]),
    (DATE_DESC, DATE_VALUES,
     [(1, '1-21-2013'), (2, '15 Aug 2012'), (3, '20011212'),
      (5, '31'), (6, 'not_date')]),
    (NOMINAL_DESC, NOMINAL_VALUES, [])
])
def test_validate_datatype(descriptor, values, result):
    testcolumn = QcColumn(values, descriptor)
    testcolumn.validate()
    with pytest.warns(None) as recorded:
        assert testcolumn._QcColumn__datatype_violated_pairs == result
        assert recorded.list == []


@pytest.mark.parametrize('descriptor, values, result', [
    (INTEGER_DESC, INTEGER_VALUES, [(0, '1'), (3, '2'), (9, '20191212')]),
    (NUMERICAL_DESC, NUMERICAL_VALUES, [(0, '-0.12')]),
    (DATE_DESC, DATE_VALUES, [(7, '1/1/1880')]),
    (NOMINAL_DESC, NOMINAL_VALUES, [(0, 'cAtegory1'), (1, 'not_value'),
                                    (4, 'another1'), (8, 'CATEGORY2')])
])
def test_validate_contraint(descriptor, values, result):
    testcolumn = QcColumn(values, descriptor)
    testcolumn.validate()
    with pytest.warns(None) as recorded:
        assert testcolumn._QcColumn__constraint_violated_pairs == result
        assert recorded.list == []


@pytest.mark.parametrize('descriptor, values, result', [
    (INTEGER_DESC, INTEGER_VALUES, ['', '', '5']),
    (NUMERICAL_DESC, NUMERICAL_VALUES, ['', '']),
    (DATE_DESC, DATE_VALUES, ['21/01/2013', '15/08/2012', '12/12/2001', '', '']),
    (NOMINAL_DESC, NOMINAL_VALUES, [])
 ])
def test_suggestions_d(descriptor, values, result):
    testcolumn = QcColumn(values, descriptor)
    testcolumn.validate()
    testcolumn.suggest_corrections()
    totest = [sugestion.newvalue
              for sugestion in testcolumn._QcColumn__dsuggestions]
    with pytest.warns(None) as recorded:
        assert totest == result
        assert recorded.list == []


@pytest.mark.parametrize('descriptor, values, result', [
    (INTEGER_DESC, INTEGER_VALUES, ['', '', '']),
    (NUMERICAL_DESC, NUMERICAL_VALUES, ['']),
    (DATE_DESC, DATE_VALUES, ['']),
    (NOMINAL_DESC, NOMINAL_VALUES, ['Category1', '', 'Another3',
                                    'Category2'])
 ])
def test_suggestions_c(descriptor, values, result):
    testcolumn = QcColumn(values, descriptor)
    testcolumn.validate()
    testcolumn.suggest_corrections()
    totest = [sugestion.newvalue
              for sugestion in testcolumn._QcColumn__csuggestions]
    with pytest.warns(None) as recorded:
        assert totest == result
        assert recorded.list == []


@pytest.mark.parametrize('descriptor, values, result', [
    (INTEGER_DESC, INTEGER_VALUES, [4, 1]),
    (NUMERICAL_DESC, NUMERICAL_VALUES, [3, 2]),
    (DATE_DESC, DATE_VALUES, [1, 1]),
    (NOMINAL_DESC, NOMINAL_VALUES, [3, 2])
])
def test_calc_stats_nocorrection(descriptor, values, result):
    testcolumn = QcColumn(values, descriptor)
    testcolumn.validate()
    testcolumn.calc_stats()
    totest = []
    totest.append(testcolumn.stats['not_nulls'])
    totest.append(testcolumn.stats['null_total'])
    with pytest.warns(None) as recorded:
        assert totest == result
        assert recorded.list == []

@pytest.mark.parametrize('descriptor, values, result', [
    (INTEGER_DESC, INTEGER_VALUES, [5, 6]),
    (NUMERICAL_DESC, NUMERICAL_VALUES, [3, 5]),
    (DATE_DESC, DATE_VALUES, [4, 4]),
    (NOMINAL_DESC, NOMINAL_VALUES, [6, 3])
])
def test_calc_stats_withcorrection(descriptor, values, result):
    testcolumn = QcColumn(values, descriptor)
    testcolumn.validate()
    testcolumn.suggest_corrections()
    testcolumn.apply_corrections()
    testcolumn.calc_stats()
    totest = []
    totest.append(testcolumn.stats['not_nulls'])
    totest.append(testcolumn.stats['null_total'])
    with pytest.warns(None) as recorded:
        assert totest == result
        assert recorded.list == []


@pytest.mark.parametrize('descriptor, values, result', [
    (INTEGER_DESC, INTEGER_VALUES,
     set([('2.5', ''), ('not_int', ''), ('5.6', '5')]))
])
def test_dcorrections(descriptor, values, result):
    testcolumn = QcColumn(values, descriptor)
    testcolumn.validate()
    testcolumn.suggest_corrections()
    with pytest.warns(None) as recorded:
        assert testcolumn.dcorrections == result
        assert recorded.list == []