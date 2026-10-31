entity FIFO is
generic ( a : integer );
end entity FIFO;

entity FIFO is
generic (
    a : integer
);
end entity FIFO;

entity FIFO is
generic
( a : integer
)
;
end entity FIFO;

-- VHDL-2019 allows a semicolon after the last interface element
entity FIFO is
  generic (
    G_A : integer := 1;
  );
end entity FIFO;
