entity FIFO is
port ( a : integer );
end entity FIFO;

entity FIFO is
port (
    a : integer
);
end entity FIFO;

entity FIFO is
port
( a : integer
)
;
end entity FIFO;

-- VHDL-2019 allows a semicolon after the last interface element
entity FIFO is
  port (
    a : in integer;
    b : out integer;
  );
end entity FIFO;
