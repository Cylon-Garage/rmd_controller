import gradio as gr
from RMDLIb import RMD

motor_id = 1
rmd = RMD('/dev/ttyUSB0', id=motor_id, baudrate=115200)


def set_goal_position(p):
    rmd.run_position1(p * 100)


def set_goal_position_0():
    p = 0
    rmd.run_position1(p * 100)
    return gr.update(value=p)


def set_goal_position_180():
    p = 180
    rmd.run_position1(p * 100)
    return gr.update(value=p)


def set_goal_position_360():
    p = 360
    rmd.run_position1(p * 100)
    return gr.update(value=p)


def incr_pos():
    p = 10
    rmd.run_increment1(int(p * 100))
    return gr.update(value=p)


def incr_neg():
    p = -10
    rmd.run_increment1(p * 100)
    return gr.update(value=p)


with gr.Blocks() as ui:

    btn_on = gr.Button(value='motor on')
    btn_on.click(rmd.motor_on, inputs=[], outputs=[])

    btn_off = gr.Button(value='motor off')
    btn_off.click(rmd.motor_stop, inputs=[], outputs=[])

    # btn_zero = gr.Button(value='motor zero')
    # btn_zero.click(motor_zero, inputs=[], outputs=[])

    with gr.Group():
        btn_p_0 = gr.Button(value='0')
        btn_p_180 = gr.Button(value='180')
        btn_p_360 = gr.Button(value='360')

    btn_incr_pos = gr.Button(value='+10deg')
    btn_incr_pos.click(incr_pos, inputs=[], outputs=[])
    btn_incr_neg = gr.Button(value='-10deg')
    btn_incr_neg.click(incr_neg, inputs=[], outputs=[])

    sld1 = gr.Slider(-360, 360, value=0, label='position [deg]')
    sld1.change(set_goal_position, inputs=sld1, outputs=[])
    position_slider = sld1

    btn_p_0.click(set_goal_position_0, inputs=[], outputs=sld1)
    btn_p_180.click(set_goal_position_180, inputs=[], outputs=sld1)
    btn_p_360.click(set_goal_position_360, inputs=[], outputs=sld1)
if __name__ == "__main__":
    ui.launch()
