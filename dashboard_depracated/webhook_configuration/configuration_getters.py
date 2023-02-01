def get_limit_forced_offset(parent_object):
    on_off_switch_col, limit_forced_offset_col = parent_object.columns(2)
    on_off_switch = on_off_switch_col.checkbox("Limit Forced Offset")

    if on_off_switch:
        limit_forced_offset = limit_forced_offset_col.slider("Limit Forced Offset", min_value=0, max_value=1.0, value=0,
                                                             step=0.01)
        return limit_forced_offset
    else:
        return -1