# RMD Style Motor Driver Python Interface (RS485 Version)

## Motor Driver

This driver controller is based on [py_rmd_servo](https://github.com/cHemingway/py_rmd_servo) by [cHemingway](https://github.com/cHemingway). I modified and extended it specifically for the [RMD-S series motor](https://www.myactuator.com/product-page/rmd-s-4005) which is supposed to come with a **DRC03 V2 driver**. However, the driver identifies itself as a **DRD02-S8** with version 1.7 firmware 🤷. This should work with RMD-S, RMD-L and many other Chinese BLDC motor drivers (maybe with some slight modifications). I've looked at many different driver manuals and a lot of them are using the same protocols.

This code is for the RS485 version of the driver. There is an option to get the driver with can-bus but this code will not work with it.

<figure>
<p align="center">
<img src="https://github.com/Cylon-Garage/rmd_controller/blob/master/driver.png?raw=true" alt="Trulli" style="width:50%">
</p>
<figcaption align="center"><b>RMD-S-4005 motor driver</b></figcaption>
</figure>

## Test GUI

I'm using [Gradio](https://gradio.app/) as a quick-and-dirty way to get a working GUI to test out the functions of the motor. It's not exactly what Gradio was meant for but it does a great job and also looks clean.
