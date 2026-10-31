--------------------------------------------------------------------------------
0 |
--------------------------------------------------------------------------------
1 |
<class 'mhsg.parser.blank_line'>
--------------------------------------------------------------------------------
2 | architecture rtl of fifo is
<class 'mhsg.token.architecture_body.architecture_keyword'>
<class 'mhsg.token.architecture_body.identifier'>
<class 'mhsg.token.architecture_body.of_keyword'>
<class 'mhsg.token.architecture_body.entity_name'>
<class 'mhsg.token.architecture_body.is_keyword'>
--------------------------------------------------------------------------------
3 |
<class 'mhsg.parser.blank_line'>
--------------------------------------------------------------------------------
4 | begin
<class 'mhsg.token.architecture_body.begin_keyword'>
--------------------------------------------------------------------------------
5 |
<class 'mhsg.parser.blank_line'>
--------------------------------------------------------------------------------
6 |   a <= b('0');
<class 'mhsg.token.concurrent_simple_signal_assignment.target'>
<class 'mhsg.token.concurrent_simple_signal_assignment.assignment'>
<class 'mhsg.token.todo.name'>
<class 'mhsg.token.todo.open_parenthesis'>
<class 'mhsg.parser.character_literal'>
<class 'mhsg.token.todo.close_parenthesis'>
<class 'mhsg.token.concurrent_simple_signal_assignment.semicolon'>
--------------------------------------------------------------------------------
7 |
<class 'mhsg.parser.blank_line'>
--------------------------------------------------------------------------------
8 |   a <= b(x, y, z);
<class 'mhsg.token.concurrent_simple_signal_assignment.target'>
<class 'mhsg.token.concurrent_simple_signal_assignment.assignment'>
<class 'mhsg.token.todo.name'>
<class 'mhsg.token.todo.open_parenthesis'>
<class 'mhsg.parser.todo'>
<class 'mhsg.parser.comma'>
<class 'mhsg.parser.todo'>
<class 'mhsg.parser.comma'>
<class 'mhsg.parser.todo'>
<class 'mhsg.token.todo.close_parenthesis'>
<class 'mhsg.token.concurrent_simple_signal_assignment.semicolon'>
--------------------------------------------------------------------------------
9 |
<class 'mhsg.parser.blank_line'>
--------------------------------------------------------------------------------
10 |   a <= b(x(3, 4, 5), y(6, 7, 8), z(9, 0, 1));
<class 'mhsg.token.concurrent_simple_signal_assignment.target'>
<class 'mhsg.token.concurrent_simple_signal_assignment.assignment'>
<class 'mhsg.token.todo.name'>
<class 'mhsg.token.todo.open_parenthesis'>
<class 'mhsg.token.todo.name'>
<class 'mhsg.token.todo.open_parenthesis'>
<class 'mhsg.parser.todo'>
<class 'mhsg.parser.comma'>
<class 'mhsg.parser.todo'>
<class 'mhsg.parser.comma'>
<class 'mhsg.parser.todo'>
<class 'mhsg.token.todo.close_parenthesis'>
<class 'mhsg.parser.comma'>
<class 'mhsg.token.todo.name'>
<class 'mhsg.token.todo.open_parenthesis'>
<class 'mhsg.parser.todo'>
<class 'mhsg.parser.comma'>
<class 'mhsg.parser.todo'>
<class 'mhsg.parser.comma'>
<class 'mhsg.parser.todo'>
<class 'mhsg.token.todo.close_parenthesis'>
<class 'mhsg.parser.comma'>
<class 'mhsg.token.todo.name'>
<class 'mhsg.token.todo.open_parenthesis'>
<class 'mhsg.parser.todo'>
<class 'mhsg.parser.comma'>
<class 'mhsg.parser.todo'>
<class 'mhsg.parser.comma'>
<class 'mhsg.parser.todo'>
<class 'mhsg.token.todo.close_parenthesis'>
<class 'mhsg.token.todo.close_parenthesis'>
<class 'mhsg.token.concurrent_simple_signal_assignment.semicolon'>
--------------------------------------------------------------------------------
11 |
<class 'mhsg.parser.blank_line'>
--------------------------------------------------------------------------------
12 |   a <= (x(3, 4, 5), y(6, 7, 8), z(9, 0, 1));
<class 'mhsg.token.concurrent_simple_signal_assignment.target'>
<class 'mhsg.token.concurrent_simple_signal_assignment.assignment'>
<class 'mhsg.token.aggregate.open_parenthesis'>
<class 'mhsg.token.todo.name'>
<class 'mhsg.token.todo.open_parenthesis'>
<class 'mhsg.parser.todo'>
<class 'mhsg.parser.comma'>
<class 'mhsg.parser.todo'>
<class 'mhsg.parser.comma'>
<class 'mhsg.parser.todo'>
<class 'mhsg.token.todo.close_parenthesis'>
<class 'mhsg.parser.comma'>
<class 'mhsg.token.todo.name'>
<class 'mhsg.token.todo.open_parenthesis'>
<class 'mhsg.parser.todo'>
<class 'mhsg.parser.comma'>
<class 'mhsg.parser.todo'>
<class 'mhsg.parser.comma'>
<class 'mhsg.parser.todo'>
<class 'mhsg.token.todo.close_parenthesis'>
<class 'mhsg.parser.comma'>
<class 'mhsg.token.todo.name'>
<class 'mhsg.token.todo.open_parenthesis'>
<class 'mhsg.parser.todo'>
<class 'mhsg.parser.comma'>
<class 'mhsg.parser.todo'>
<class 'mhsg.parser.comma'>
<class 'mhsg.parser.todo'>
<class 'mhsg.token.todo.close_parenthesis'>
<class 'mhsg.token.aggregate.close_parenthesis'>
<class 'mhsg.token.concurrent_simple_signal_assignment.semicolon'>
--------------------------------------------------------------------------------
13 |
<class 'mhsg.parser.blank_line'>
--------------------------------------------------------------------------------
14 |   a <= ((3, 4, 5), (6, 7, 8), (9, 0, 1));
<class 'mhsg.token.concurrent_simple_signal_assignment.target'>
<class 'mhsg.token.concurrent_simple_signal_assignment.assignment'>
<class 'mhsg.token.aggregate.open_parenthesis'>
<class 'mhsg.token.aggregate.open_parenthesis'>
<class 'mhsg.parser.todo'>
<class 'mhsg.parser.comma'>
<class 'mhsg.parser.todo'>
<class 'mhsg.parser.comma'>
<class 'mhsg.parser.todo'>
<class 'mhsg.token.aggregate.close_parenthesis'>
<class 'mhsg.parser.comma'>
<class 'mhsg.token.aggregate.open_parenthesis'>
<class 'mhsg.parser.todo'>
<class 'mhsg.parser.comma'>
<class 'mhsg.parser.todo'>
<class 'mhsg.parser.comma'>
<class 'mhsg.parser.todo'>
<class 'mhsg.token.aggregate.close_parenthesis'>
<class 'mhsg.parser.comma'>
<class 'mhsg.token.aggregate.open_parenthesis'>
<class 'mhsg.parser.todo'>
<class 'mhsg.parser.comma'>
<class 'mhsg.parser.todo'>
<class 'mhsg.parser.comma'>
<class 'mhsg.parser.todo'>
<class 'mhsg.token.aggregate.close_parenthesis'>
<class 'mhsg.token.aggregate.close_parenthesis'>
<class 'mhsg.token.concurrent_simple_signal_assignment.semicolon'>
--------------------------------------------------------------------------------
15 |
<class 'mhsg.parser.blank_line'>
--------------------------------------------------------------------------------
16 |   a <= a, b;
<class 'mhsg.token.concurrent_simple_signal_assignment.target'>
<class 'mhsg.token.concurrent_simple_signal_assignment.assignment'>
<class 'mhsg.parser.todo'>
<class 'mhsg.token.waveform.comma'>
<class 'mhsg.parser.todo'>
<class 'mhsg.token.concurrent_simple_signal_assignment.semicolon'>
--------------------------------------------------------------------------------
17 |
<class 'mhsg.parser.blank_line'>
--------------------------------------------------------------------------------
18 |   a <= b(x => 3, y => 2, z => 1);
<class 'mhsg.token.concurrent_simple_signal_assignment.target'>
<class 'mhsg.token.concurrent_simple_signal_assignment.assignment'>
<class 'mhsg.token.todo.name'>
<class 'mhsg.token.todo.open_parenthesis'>
<class 'mhsg.parser.todo'>
<class 'mhsg.token.element_association.assignment'>
<class 'mhsg.parser.todo'>
<class 'mhsg.parser.comma'>
<class 'mhsg.parser.todo'>
<class 'mhsg.token.element_association.assignment'>
<class 'mhsg.parser.todo'>
<class 'mhsg.parser.comma'>
<class 'mhsg.parser.todo'>
<class 'mhsg.token.element_association.assignment'>
<class 'mhsg.parser.todo'>
<class 'mhsg.token.todo.close_parenthesis'>
<class 'mhsg.token.concurrent_simple_signal_assignment.semicolon'>
--------------------------------------------------------------------------------
19 |
<class 'mhsg.parser.blank_line'>
--------------------------------------------------------------------------------
20 | end architecture;
<class 'mhsg.token.architecture_body.end_keyword'>
<class 'mhsg.token.architecture_body.end_architecture_keyword'>
<class 'mhsg.token.architecture_body.semicolon'>
