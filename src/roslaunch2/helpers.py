#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Author: Adrian Böckenkamp
# License: BSD (https://opensource.org/licenses/BSD-3-Clause)
#    Date: 12/11/2019

import logger
import node


class Helpers:
    @staticmethod
    def __warn_if_not_empty(n):
        """
        Warns if the provided prefix is not empty.

        :param n: The roslaunch2.node.Node instance to be used
        """
        assert isinstance(n, node.Node)
        if n.prefix is not None:
            logger.warning("Node.prefix is not empty, overwriting existing prefix '{}' (only one can be active at a"
                           " time).".format(n.prefix))

    @staticmethod
    def enable_callgrind(node):
        """
        Enable CPU profiling using valgrind's "callgrind" buildin tool. Must be installed using
        :code:`sudo apt install valgrind`. Callgrind is a profiling tool that records the call history among function in
        UNIX process. The profile data is written out to a file named :code:`callgrind.[node_name].[pid]` at program
        termination. The data files generated by Callgrind can be loaded into Kcachegrind (GUI) for browsing the performance results
        using :code:`kcachegrind ~/.ros/callgrind.[node_name].[pid]`. Kcachegrind can be installed using
        :code:`sudo apt install kcachegrind`.

        :param node: The roslaunch2.node.Node instance to be used
        """
        Helpers.__warn_if_not_empty(node)
        node.prefix = "valgrind --tool=callgrind --callgrind-out-file='callgrind.{}.%p'".format(node.name)

    @staticmethod
    def enable_nice(node):
        """
        Nice your process to lower its CPU usage.

        :param node: The roslaunch2.node.Node instance to be used
        """
        Helpers.__warn_if_not_empty(node)
        node.prefix = "nice"

    @staticmethod
    def enable_gdb(node, separate_window=True):
        """
        Debug your ROS node using gdb (for roscpp, not rospy). You should compile your code in DEBUG mode (e. g., add
        :code:`-g` flag in gcc). Requires :code:`sudo apt install xterm` if :code:`separate_window=True`.

        :param node: The roslaunch2.node.Node instance to be debugged
        :param separate_window: :code:`True` to open the GDB session in a new window (manually type :code:`run` to start
               it), :code:`False` otherwise (will start right away, without having to type anything to start it)
        """
        Helpers.__warn_if_not_empty(node)
        if separate_window:
            node.prefix = "xterm -e gdb --args"
        else:
            node.prefix = "gdb -ex run --args"

    @staticmethod
    def enable_valgrind(node):
        """
        Check for memory leaks using valgrind. Must be installed using :code:`sudo apt install valgrind`.

        :param node: The roslaunch2.node.Node instance to be analyzed
        """
        Helpers.__warn_if_not_empty(node)
        node.prefix = "valgrind"

    @staticmethod
    def enable_separate_window(node):
        """
        Run the node in a separate window using xterm. All output is just printed in this separate window, making it
        easier to read. Requires :code:`sudo apt install xterm`.

        :param node: The roslaunch2.node.Node instance to be executed
        """
        Helpers.__warn_if_not_empty(node)
        node.prefix = "xterm -e"

    @staticmethod
    def enable_pdb(node):
        """
        Debug your ROS node using pdb (for rospy, not roscpp). You have to manually type :code:`run` to start it.
        Requires :code:`sudo apt install xterm`.

        :param node: The roslaunch2.node.Node instance to be debugged
        """
        Helpers.__warn_if_not_empty(node)
        node.prefix = "xterm -e python -m pdb"
