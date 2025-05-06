import vec
import vec.vec as vec2
import time

VECTOR_VALUE = 1.2

start_var = time.monotonic_ns()
a = vec2.Vector(VECTOR_VALUE)
end_var = time.monotonic_ns()
start_sum = time.monotonic_ns()
for i in range(100000):
    a+= a
end_sum = time.monotonic_ns()
print(f"Pure python variable creation time was {(end_var-start_var)/10e3} µs")
print(f"Pure python sum time was {(end_sum-start_sum)/10e3} µs")

start_var_c = time.monotonic_ns()
a = vec.Vector(VECTOR_VALUE)
end_var_c = time.monotonic_ns()
start_sum_c = time.monotonic_ns()
for i in range(100000):
    a+= a
end_sum_c = time.monotonic_ns()
print(f"Cython variable creation time was {(end_var_c-start_var_c)/10e3} µs")
print(f"Cython sum time was {(end_sum_c-start_sum_c)/10e3} µs")

print(f"Cython is {round((end_sum-start_sum)/(end_sum_c-start_sum_c), 2)} times faster than pure python.")

i=0
loop_time_counter = 0.0
loop_start = time.monotonic_ns()
while 1.0:
    loop_end = time.monotonic_ns()
    loop_time_counter+= loop_end-loop_start
    i+=1
    if i>=100000:
        break
    loop_start = time.monotonic_ns()

print(f"Loop time with float is {loop_time_counter/10e3} µs")

i=0
loop_time_counter = 0.0
loop_start = time.monotonic_ns()
while 2:
    loop_end = time.monotonic_ns()
    loop_time_counter+= loop_end-loop_start
    i+=1
    if i>=100000:
        break
    loop_start = time.monotonic_ns()

print(f"Loop time with int is {loop_time_counter/10e3} µs")
