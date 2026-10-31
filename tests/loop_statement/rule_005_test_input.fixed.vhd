
architecture RTL of FIFO is

begin

  process
  begin

    LOOP_LABEL: loop end loop;

    LOOP_LABEL: while condition loop end loop;

    LOOP_LABEL: for x in range(15 downto 0) loop end loop;


    LOOP_LABEL:      loop end loop;

    LOOP_LABEL:      while condition loop end loop;

    LOOP_LABEL:      for x in range(15 downto 0) loop end loop;

    -- Comments between label and loop should not be merged (issue 1585)
    LOOP_LABEL:
      -- first comment
      -- second comment
      loop end loop;

  end process;

end;
