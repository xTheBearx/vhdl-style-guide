
package body pkg is

  type t_mem is protected body

    type t_state is (IDLE,
      BUSY);

    type t_mode is (READ,
      WRITE);

    procedure p is
    begin
    end procedure p;

  end protected body t_mem ;

end package body pkg;
