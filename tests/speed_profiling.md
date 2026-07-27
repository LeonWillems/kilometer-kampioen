To profile the speed of the code using cProfile, run the following command in the terminal:
`python -m cProfile -o speed.prof -m run`

Run the following in any case to inspect the results:
`snakeviz ./speed.prof`