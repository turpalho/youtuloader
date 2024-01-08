import logging
import traceback

def exception_hook(exc_type, exc_value, tb, *args):
    # local_vars = {}
    # while tb:
    #     filename = tb.tb_frame.f_code.co_filename
    #     name = tb.tb_frame.f_code.co_name
    #     line_no = tb.tb_lineno
    #     logging.error(f"File {filename} line {line_no}, in {name}")
    #     local_vars = tb.tb_frame.f_locals
    #     tb = tb.tb_next
    # logging.error(f"Local variables in top frame: {local_vars}")
    # logging.error(f"Error type: {exc_type.__name__}")
    logging.error("Full traceback:\n%s", traceback.format_exc())