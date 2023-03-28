import tkinter as tk
from datetime import datetime, timedelta, date
# input cal1 9:00-10:30; 12:00-13:00; 16:00-18:00
#input cal2 10:00-11:30; 12:30-14:30; 14:30-15:00; 16:00-17:00


class CalendarApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Calendar App")

        # Create labels and entry boxes for input
        tk.Label(master, text="Calendar 1").grid(row=0, column=0)
        tk.Label(master, text="Booked Time").grid(row=1, column=0)
        tk.Label(master, text="Min Range").grid(row=2, column=0)
        tk.Label(master, text="Max Range").grid(row=3, column=0)
        self.output_text = tk.Text(master, height=1, width=50)
        self.output_text.grid(row=7, column=0, columnspan=7)

        self.cal1_booked_entry = tk.Entry(master)
        self.cal1_booked_entry.grid(row=1, column=1)

        self.cal1_min_entry = tk.Entry(master)
        self.cal1_min_entry.grid(row=2, column=1)

        self.cal1_max_entry = tk.Entry(master)
        self.cal1_max_entry.grid(row=3, column=1)

        tk.Label(master, text="Calendar 2").grid(row=0, column=2)
        tk.Label(master, text="Booked Time").grid(row=1, column=2)
        tk.Label(master, text="Min Range").grid(row=2, column=2)
        tk.Label(master, text="Max Range").grid(row=3, column=2)

        self.cal2_booked_entry = tk.Entry(master)
        self.cal2_booked_entry.grid(row=1, column=3)

        self.cal2_min_entry = tk.Entry(master)
        self.cal2_min_entry.grid(row=2, column=3)

        self.cal2_max_entry = tk.Entry(master)
        self.cal2_max_entry.grid(row=3, column=3)

        tk.Label(master, text="Meeting Time (min)").grid(row=4, column=0)
        self.meeting_time_entry = tk.Entry(master)
        self.meeting_time_entry.grid(row=4, column=1, columnspan=3)

        # Create button to find available time
        tk.Button(master, text="Find Available Time", command=self.find_available_time).grid(row=5, column=1,
                                                                                             columnspan=2)

        # Create label to display result
        self.result_label = tk.Label(master, text="")
        self.result_label.grid(row=6, column=0, columnspan=4)

    def str_to_datetime(self, time_str):
        if '-' in time_str:
            # Handle input string with hyphen separator
            start_time, end_time = time_str.split('-')
            start_time = datetime.strptime(start_time.strip(), '%H:%M')
            end_time = datetime.strptime(end_time.strip(), '%H:%M')
            return datetime.combine(date.today(), start_time.time()), datetime.combine(date.today(), end_time.time())
        else:
            # Handle input string without hyphen separator
            return datetime.combine(date.today(), datetime.strptime(time_str, '%H:%M').time())
    def datetime_to_str(self, dt):
        return dt.strftime('%H:%M')

    def datetime_range(self, start, end, interval):
        current = start
        while current < end:
            yield current
            current += interval
        yield end

    def find_available_time(self):
        # Get input values from entry boxes
        cal1_booked = self.cal1_booked_entry.get()
        cal1_min = self.cal1_min_entry.get()
        cal1_max = self.cal1_max_entry.get()
        cal2_booked = self.cal2_booked_entry.get()
        cal2_min = self.cal2_min_entry.get()
        cal2_max = self.cal2_max_entry.get()
        meeting_time = int(self.meeting_time_entry.get())

        # Convert input values to datetime objects
        cal1_booked = [self.str_to_datetime(t) for t in cal1_booked.split(";")]
        cal1_min = self.str_to_datetime(cal1_min)
        cal1_max = self.str_to_datetime(cal1_max)
        cal2_booked = [self.str_to_datetime(t) for t in cal2_booked.split(";")]
        cal2_min = self.str_to_datetime(cal2_min)
        cal2_max = self.str_to_datetime(cal2_max)

        # Find free time between the two calendars
        free_time = []
        start_time = max(cal1_min, cal2_min)
        end_time = min(cal1_max, cal2_max)

        # Check if there is any overlapping booked time in the two calendars
        overlapping_time = []
        for c1_start, c1_end in cal1_booked:
            for c2_start, c2_end in cal2_booked:
                overlap_start = max(c1_start, c2_start)
                overlap_end = min(c1_end, c2_end)
                if overlap_start < overlap_end:
                    overlapping_time.append((overlap_start, overlap_end))

        # Loop through the free time between the two calendars
        current_time = start_time
        while current_time < end_time:
            # Check if the current time is overlapping booked time
            is_overlapping = False
            for overlap_start, overlap_end in overlapping_time:
                if current_time < overlap_end and overlap_start < current_time + timedelta(minutes=meeting_time):
                    is_overlapping = True
                    current_time = overlap_end
                    break

            # If the current time is not overlapping booked time, add it to free_time
            if not is_overlapping:
                free_end_time = current_time + timedelta(minutes=meeting_time)
                if free_end_time <= end_time:
                    free_time.append((current_time, free_end_time))
                current_time = free_end_time

        # Remove busy intervals from free time
        busy_intervals = []
        for c1_start, c1_end in cal1_booked:
            busy_intervals.extend(
                [(t, t + timedelta(minutes=1)) for t in self.datetime_range(c1_start, c1_end, timedelta(minutes=1))])
        for c2_start, c2_end in cal2_booked:
            busy_intervals.extend(
                [(t, t + timedelta(minutes=1)) for t in self.datetime_range(c2_start, c2_end, timedelta(minutes=1))])

        free_time_filtered = []
        for i in range(len(cal1_booked)-1):
            start1, end1 = cal1_booked[i]
            interval1 = 0
            interval2 = 0
            for f_start, f_end in free_time:
                if end1 >= f_start:
                    interval1=end1
                    next_start, next_end = cal1_booked[i + 1]
                    interval2=next_start
                    free_time_filtered.append((interval1,interval2))
                    if i==len(cal1_booked)-2 and next_end<cal1_max:
                        free_time_filtered.append((next_end,cal1_max))
                    break
        perfect_time=[]
        for i in range(len(cal2_booked)-1):
            start2, end2 = cal2_booked[i]
            for j in range(len(free_time_filtered)):
                f_start,f_end=free_time_filtered[j]
                if end2>f_end:
                    continue
                next_start, next_end = cal2_booked[i + 1]
                if end2!=next_start:
                    perfect_time.append((end2,f_end))
                if i == len(cal2_booked)-2:
                    f_start, f_end = free_time_filtered[len(free_time_filtered)-1]
                    if next_end<=f_start:
                        perfect_time.append((f_start,end_time))
                break
        # Display the free time in the output text box
        perfect_time_2=[]
        for start,end in perfect_time:
            hour=end-start
            minutes=hour.total_seconds()/60
            if minutes>=meeting_time:
                perfect_time_2.append((start,end))
        perfect_time_2 = [[self.datetime_to_str(start), self.datetime_to_str(end)] for start, end in perfect_time_2]



        self.output_text.delete('1.0', tk.END)
        if perfect_time_2:
            for start, end in perfect_time_2:
                self.output_text.insert(tk.END, f"{start} - {end};")
        else:
            self.output_text.insert(tk.END, "No available time for the meeting.\n")