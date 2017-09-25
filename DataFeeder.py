import threading, tensorflow as tf

def build_feeder(prepare_batch_func, coordinator, placeholders, batch_size=32):
    """
    Helper function for building data feeder.
    :param prepare_batch_func:
    :param coordinator: tensorflow.train.Coordinator instance
    :param placeholders: list of tensorflow.placeholder instance
    :param batch_size:
    :return:
    """
    base_feeder = BaseFeeder(coordinator, placeholders, batch_size)
    base_feeder.prepare_batch = prepare_batch_func
    base_feeder.start()
    return base_feeder

class BaseFeeder(threading.Thread):
    def __init__(self, coordinator, placeholders, batch_size=32):
        """

        :param coordinator:
        :param placeholders:
        :param batch_size:
        """
        self.coord = coordinator
        self.queue = tf.FIFOQueue(capacity=int(batch_size/4), dtypes=[item.dtype for item in placeholders])
        self.enqueue_op = self.queue.enqueue(placeholders)
        self.fed_holders = [deq.set_shape(ph.get_shape()) for deq, ph in zip(self.queue.dequeue(), placeholders)]

    def prepare_batch(self):
        pass

    def run(self):
        try:
            while not self.coord.should_stop:
                self.prepare_batch()
        except Exception as e:
            # Report exceptions to the coordinator.
            self.coord.request_stop(e)
        finally:
            # Terminate as usual. It is safe to call `coord.request_stop()` twice.
            self.coord.request_stop()
