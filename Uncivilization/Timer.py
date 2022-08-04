import time


class Timer:
    def __init__(self):
        self.object_t0 = time.time()
        self.current_t0 = None
        self.paused_time = 0
        self.paused_t0 = None
        self.is_paused = False
        self.inactive = True
        self.last_timer_tot_runtime = None
        self.last_timer_tot_pausetime = None

    def start_timer(self):
        # if self.current_t0:
        #     print("Timer already started")

        # if self.is_paused:
        #     print("Cannot start paused timer")

        if self.is_paused is False and self.current_t0 is None:
            # print("starting timer")
            self.current_t0 = time.time()
            self.inactive = False

    def end_timer(self):
        # if self.inactive:
        #     print("Cannot end an inactive timer")

        dt = None

        if self.is_paused:
            self.resume_timer()
            # print("Timer paused, resuming then ending")

        if self.current_t0:
            dt = time.time() - self.current_t0 - self.paused_time
            self.current_t0 = None
            self.last_timer_tot_runtime = dt
            self.last_timer_tot_pausetime = self.paused_time
            self.paused_time = 0
            self.inactive = True
            # print("ending timer")
        return dt

    def pause_timer(self):
        # if self.is_paused:
        #     print("Timer is already Paused")

        # if self.inactive:
        #     print("Cannot pause inactive timer")

        if not self.is_paused and not self.inactive:
            self.paused_t0 = time.time()
            self.is_paused = True
            # print("Pausing timer")

    def resume_timer(self):
        # if not self.is_paused:
        #     print("Can only resume a paused timer")

        # if self.inactive:
        #     print("cannot resume an inactive timer")

        if self.is_paused and not self.inactive:
            self.paused_time += time.time() - self.paused_t0
            self.is_paused = False
            self.paused_t0 = None
            # print("Resuming Timer")

    def peek_timer(self):
        dt = (
            time.time() - self.current_t0 - self.paused_time
            if self.current_t0 is not None
            else None
        )
        dt2 = time.time() - self.paused_t0 if self.paused_t0 is not None else None
        return dt, dt2

    def smart_peek_timer(self):
        t = 0
        current_pause_not_included, current_pause = self.peek_timer()
        if current_pause_not_included:
            t = (
                current_pause_not_included - current_pause
                if current_pause
                else current_pause_not_included
            )
        return t

    def exceeds_time(self, timeout):
        return True if self.smart_peek_timer() > timeout else False

    def stop_if_exceeds_time(self, timeout):
        is_over_time = self.exceeds_time(timeout)
        if is_over_time:
            self.end_timer()
        return not is_over_time

    def true_timer(self, timeout):
        if self.inactive:
            self.start_timer()
        return self.stop_if_exceeds_time(timeout)

    def get_obj_lifetime(self):
        return time.time() - self.object_t0
