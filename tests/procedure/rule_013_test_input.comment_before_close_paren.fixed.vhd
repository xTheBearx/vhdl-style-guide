
package pkg is

  procedure proc (
    arg : natural); -- Here:

end package pkg;

package body pkg is

  procedure proc (
    arg : natural) is -- And here:

  begin

    null;

  end procedure proc;

end package body pkg;

package p is
  procedure p1 (
    a : natural -- c1
  ); -- c2
end package p;
