"""
Tentative Analyzer for a UXsim++ simulation result.
Adapted from UXsim https://github.com/toruseo/UXsim/blob/main/uxsim/analyzer.py

This module is automatically loaded when you import the `uxsim` module.
"""

import random
import warnings
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import glob, os, csv, time
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from PIL.Image import Resampling
from tqdm.auto import tqdm
from collections import defaultdict as ddict
from importlib.resources import files
from pathlib import Path
import io
from scipy.sparse.csgraph import floyd_warshall

from .utils import *

def gen_unique_color(integer_id, rgb_tuple=False):
    """
    Generate a unique color code in the format '#xxxxxx' for a given integer ID.

    Parameters
    ----------
    integer_id : int
        Integer ID to generate color for.
    rgb_tuple : bool, optional
        If True, return RGB tuple instead of hex string. Default is False.

    Returns
    -------
    str or tuple
        Color code in hex format or RGB tuple.
    """
    # Use a simple hash function to generate deterministic but seemingly random values
    h = integer_id * 1103515245 + 12345
    h = (h & 0x7FFFFFFF)  # 32-bit positive integer
    
    # Extract values for RGB (avoiding very light colors)
    r = (h % 200)  # 0-199 range
    h = (h // 200)
    g = (h % 200)  # 0-199 range
    h = (h // 200)
    b = (h % 200)  # 0-199 range
    
    # Convert to hex format
    if rgb_tuple:
        return r,g,b
    else:
        color_code = f'#{r:02x}{g:02x}{b:02x}'
        
        return color_code

#####################################################
## MARK: 各種定数

dict_VehicleState = {
    0: "home",
    1: "wait",
    2: "run",
    3: "end",
}

class Analyzer:
    """
    Class for analyzing and visualizing a simulation result.
    """

    def __init__(s, W, save_mode=True, show_mode=True, ax_return_mode=False):
        """
        Create result analysis object.

        Parameters
        ----------
        W : object
            The world to which this belongs.
        """
        s.W = W

        os.makedirs(f"out_{s.W.name}", exist_ok=True)

        #モード
        s.save_mode = save_mode
        s.show_mode = show_mode
        s.ax_return_mode = ax_return_mode

        #補間後の車両軌跡
        s.tss = ddict(list)
        s.xss = ddict(list)
        s.ls = ddict(list)
        s.names = ddict(list)
        s.cs = ddict(list)

        #フラグ
        s.flag_compute_accurate_trajectories = False

    def _compute_accurate_trajectories(s):         
        if not s.flag_compute_accurate_trajectories:  
            for veh in s.W.VEHICLES:
                l_old = None
                for i in lange(veh.log_t):
                    if veh.log_link[i] != -1:
                        l = s.W.LINKS[veh.log_link[i]]
                        if l_old != l:
                            s.tss[l].append([])
                            s.xss[l].append([])
                            s.ls[l].append(0)#veh.log_lane[i]
                            s.cs[l].append(gen_unique_color(veh.id))
                            s.names[l].append(veh.name)

                        l_old = l
                        s.tss[l][-1].append(veh.log_t[i])
                        s.xss[l][-1].append(veh.log_x[i])

            for l in s.W.LINKS:
                #端部を外挿
                for i in lange(s.xss[l]):
                    if len(s.xss[l][i]):
                        if s.xss[l][i][0] != 0:
                            x_remain = s.xss[l][i][0]
                            if x_remain/l.vmax > s.W.DELTAT*0.01:
                                s.xss[l][i].insert(0, 0)
                                s.tss[l][i].insert(0, s.tss[l][i][0]-x_remain/l.vmax)
                        if l.length-l.vmax*s.W.DELTAT <= s.xss[l][i][-1] < l.length:
                            x_remain = l.length-s.xss[l][i][-1]
                            if x_remain/l.vmax > s.W.DELTAT*0.01:
                                s.xss[l][i].append(l.length)
                                s.tss[l][i].append(s.tss[l][i][-1]+x_remain/l.vmax)
                                
            s.flag_compute_accurate_trajectories = True
    
    def plot_time_space_trajectories(s, linkslist, figsize=(12,4)):
        """
        Draws the time-space diagram of vehicle trajectories for vehicles on concective links.

        Parameters
        ----------
        linkslist : list of link or list of list of link
            The names of the concective links for which the time-space diagram is to be plotted.
        figsize : tuple of int, optional
            The size of the figure to be plotted, default is (12,4).
        """

        s._compute_accurate_trajectories()

        try:
            iter(linkslist[0])
            if type(linkslist[0]) == str:
                linkslist = [linkslist]
        except TypeError:
            linkslist = [linkslist]

        for links in linkslist:
            linkdict = dict()
            d = 0
            for ll in links:
                l = s.W.get_link(ll)
                linkdict[l] = d
                d += l.length

            plt.figure(figsize=figsize)
            for ll in links:
                l = s.W.get_link(ll)
                for i in range(len(s.xss[l])):
                    lane_shift = 0#l.s.ls[i]/l.number_of_lanes*s.W.DELTAT/2 #vehicle with the same lane is plotted slightly shifted
                    plt.plot(np.array(s.tss[l][i])+lane_shift, np.array(s.xss[l][i])+linkdict[l], "-", c=s.cs[l][i], lw=0.5)
                # if plot_signal: TODO:signal
                #     signal_log = [i*s.W.DELTAT for i in lange(l.end_node.signal_log) if (l.end_node.signal_log[i] not in l.signal_group and len(l.end_node.signal)>1)]
                #     plt.plot(signal_log, [l.length+linkdict[l] for i in lange(signal_log)], "r.")
            for l in linkdict.keys():
                plt.plot([0, s.W.TMAX], [linkdict[l], linkdict[l]], "k--", lw=0.7)
                plt.plot([0, s.W.TMAX], [linkdict[l]+l.length, linkdict[l]+l.length], "k--", lw=0.7)
                plt.text(0, linkdict[l]+l.length/2, l.name, va="center", c="b")
                plt.text(0, linkdict[l], l.start_node.name, va="center", c="g")
                plt.text(0, linkdict[l]+l.length, l.end_node.name, va="center", c="g")
            plt.xlabel("time (s)")
            plt.ylabel("space (m)")
            plt.xlim([0, s.W.TMAX])
            plt.grid()
            
        plt.tight_layout()
    
        if s.save_mode:
            if len(links) == 1:
                plt.savefig(f"out_{s.W.name}/tsd_traj_{s.W.get_link(links[0]).name}.png")
            else:
                plt.savefig(f"out_{s.W.name}/tsd_traj_links_{'-'.join([s.W.get_link(l).name for l in links])}.png")
        if s.show_mode:
            plt.show()
        else:
            plt.close("all")

    def network(s, t=None, state_variables="density_speed", minwidth=0.5, maxwidth=24, left_handed=1, tmp_anim=0, figsize=6, network_font_size=0, node_size=2, image_return=0, legend=True):

        maxx = max([n.x for n in s.W.NODES])
        minx = min([n.x for n in s.W.NODES])
        maxy = max([n.y for n in s.W.NODES])
        miny = min([n.y for n in s.W.NODES])

        scale = 2
        try:
            coef = figsize*100*scale/(maxx-minx)
        except:
            coef = figsize[0]*100*scale/(maxx-minx)
        maxx *= coef
        minx *= coef
        maxy *= coef
        miny *= coef
        minwidth *= scale
        maxwidth *= scale

        buffer = (maxx-minx)/10
        maxx += buffer
        minx -= buffer
        maxy += buffer
        miny -= buffer

        lypad = 0
        if legend:
            lypad = buffer*1.5
            miny -= lypad
        img = Image.new("RGBA", (int(maxx-minx), int(maxy-miny)), (255, 255, 255, 255))
        draw = ImageDraw.Draw(img)

        font = ImageFont.load_default(size=30)
        #font = ImageFont.truetype("arial.ttf", int(network_font_size))

        def flip(y):
            return img.size[1]-y

        for l in s.W.LINKS:
            x1, y1 = l.start_node.x*coef-minx, l.start_node.y*coef-miny
            x2, y2 = l.end_node.x*coef-minx, l.end_node.y*coef-miny
            vx, vy = (y1-y2)*0.05, (x2-x1)*0.05
            if not left_handed:
                vx, vy = -vx, -vy
            if state_variables == "density_speed":
                k = (l.cum_arrival[int(t/s.W.DELTAT)]-l.cum_departure[int(t/s.W.DELTAT)])/l.length
                v = l.length/l.traveltime_instant[int(t/s.W.DELTAT)]
                width = k*l.delta*(maxwidth-minwidth)+minwidth
                c = plt.colormaps["viridis"](v/l.u)
            else: #"flow_delay" mode
                k = (l.cum_arrival[int(t/s.W.DELTAT)]-l.cum_departure[int(t/s.W.DELTAT)])/l.length
                v = l.length/l.traveltime_instant[int(t/s.W.DELTAT)]
                q = k*v
                width = q/l.capacity*(maxwidth-minwidth)+minwidth

                pace_ratio = l.u/v    #pace (inverse of speed) is more intuitive
                pace_max = 2.0
                pace_min = 1.0
                color_coef = (pace_ratio-pace_min)/(pace_max-pace_min)
                if color_coef < 0.1:    #delay_ratio < 10%
                    color_coef = 0.1
                if color_coef > 0.9:    #delay_ratio > 90%
                    color_coef = 0.9

                c = plt.colormaps["jet"](color_coef)

                
            xmid1, ymid1 = (2*x1+x2)/3+vx, (2*y1+y2)/3+vy
            xmid2, ymid2 = (x1+2*x2)/3+vx, (y1+2*y2)/3+vy
            draw.line([(x1, flip(y1)), (xmid1, flip(ymid1)), (xmid2, flip(ymid2)), (x2, flip(y2))], fill=(int(c[0]*255), int(c[1]*255), int(c[2]*255)), width=int(width), joint="curve")

            if network_font_size > 0:
                draw.text((xmid1, flip(ymid1)), l.name, font=font, fill="blue", anchor="mm")

        for n in s.W.NODES:
            if network_font_size > 0:
                draw.text(((n.x)*coef-minx, flip((n.y)*coef-miny)), n.name, font=font, fill="green", anchor="mm")
                draw.text(((n.x)*coef-minx, flip((n.y)*coef-miny)), n.name, font=font, fill="green", anchor="mm")


        draw.text((img.size[0]/2,20), f"t = {t :>8} (s)", font=font, fill="black", anchor="mm")

        if legend:
            
            lx00 = (maxx-minx)*0.25
            lx01 = (maxx-minx)*0.35
            lx10 = (maxx-minx)*0.65
            lx11 = (maxx-minx)*0.75
            ly0 = -buffer-miny
            ly1 = -buffer-lypad*0.35-miny
            ly2 = -buffer-lypad*0.7-miny

            lny = flip(-buffer+lypad*0.2-miny)
            lsy = flip(-buffer-lypad*0.9-miny)
            lex = (maxx-minx)*0.15
            lwx = (maxx-minx)*0.87
            
            if state_variables == "density_speed":
                c1 = tuple(int(c*255) for c in plt.colormaps["viridis"](1.0))[:3]
                c2 = tuple(int(c*255) for c in plt.colormaps["viridis"](0.0))[:3]

                draw.text(((lx00+lx01)/2, flip(ly0)), "color: speed", font=font, fill="black", anchor="mm")
                draw.line([(lx00, flip(ly1)), (lx01, flip(ly1))], fill=c1, width=int((maxwidth-minwidth)/2))
                draw.line([(lx00, flip(ly2)), (lx01, flip(ly2))], fill=c2, width=int((maxwidth-minwidth)/2))            
                draw.text((lx01+10, flip(ly1)), "max", font=font, fill="black", anchor="lm")
                draw.text((lx01+10, flip(ly2)), "0", font=font, fill="black", anchor="lm")

                draw.text(((lx10+lx11)/2, flip(ly0)), "width: density", font=font, fill="black", anchor="mm")    
                draw.line([(lx10, flip(ly1)), (lx11, flip(ly1))], fill="black", width=int(minwidth))
                draw.line([(lx10, flip(ly2)), (lx11, flip(ly2))], fill="black", width=int(maxwidth))            
                draw.text((lx11+10, flip(ly1)), "0", font=font, fill="black", anchor="lm")
                draw.text((lx11+10, flip(ly2)), "max", font=font, fill="black", anchor="lm")

            elif state_variables == "density_flow":
                c1 = tuple(int(c*255) for c in plt.colormaps["magma"](1.0))[:3]
                c2 = tuple(int(c*255) for c in plt.colormaps["magma"](0.0))[:3]

                draw.text(((lx00+lx01)/2, flip(ly0)), "color: flow", font=font, fill="black", anchor="mm")
                draw.line([(lx00, flip(ly1)), (lx01, flip(ly1))], fill=c1, width=int((maxwidth-minwidth)/2))
                draw.line([(lx00, flip(ly2)), (lx01, flip(ly2))], fill=c2, width=int((maxwidth-minwidth)/2))            
                draw.text((lx01+10, flip(ly1)), "max", font=font, fill="black", anchor="lm")
                draw.text((lx01+10, flip(ly2)), "0", font=font, fill="black", anchor="lm")

                draw.text(((lx10+lx11)/2, flip(ly0)), "width: density", font=font, fill="black", anchor="mm")    
                draw.line([(lx10, flip(ly1)), (lx11, flip(ly1))], fill="black", width=int(minwidth))
                draw.line([(lx10, flip(ly2)), (lx11, flip(ly2))], fill="black", width=int(maxwidth))            
                draw.text((lx11+10, flip(ly1)), "0", font=font, fill="black", anchor="lm")
                draw.text((lx11+10, flip(ly2)), "max", font=font, fill="black", anchor="lm")

            
            else:    #"flow_delay" mode
                c1 = tuple(int(c*255) for c in plt.colormaps["jet"](0.1))[:3]
                c2 = tuple(int(c*255) for c in plt.colormaps["jet"](0.9))[:3]

                draw.text(((lx00+lx01)/2, flip(ly0)), "color: delay", font=font, fill="black", anchor="mm")
                draw.line([(lx00, flip(ly1)), (lx01, flip(ly1))], fill=c1, width=int((maxwidth-minwidth)/2))
                draw.line([(lx00, flip(ly2)), (lx01, flip(ly2))], fill=c2, width=int((maxwidth-minwidth)/2))            
                draw.text((lx01+10, flip(ly1)), "< 10%", font=font, fill="black", anchor="lm")
                draw.text((lx01+10, flip(ly2)), "> 90%", font=font, fill="black", anchor="lm")

                draw.text(((lx10+lx11)/2, flip(ly0)), "width: flow", font=font, fill="black", anchor="mm")    
                draw.line([(lx10, flip(ly1)), (lx11, flip(ly1))], fill="black", width=int(minwidth))
                draw.line([(lx10, flip(ly2)), (lx11, flip(ly2))], fill="black", width=int(maxwidth))            
                draw.text((lx11+10, flip(ly1)), "0", font=font, fill="black", anchor="lm")
                draw.text((lx11+10, flip(ly2)), "max", font=font, fill="black", anchor="lm")
            draw.line([(lwx, lny), (lex, lny), (lex, lsy), (lwx, lsy), (lwx, lny)], fill="black", width=1)

        img = img.resize((int((maxx-minx)/scale), int((maxy-miny)/scale)), resample=Resampling.LANCZOS)
        if image_return:
            return img
        elif tmp_anim:
            img.save(f"out_{s.W.name}/tmp_anim_{t}.png")
        else:
            #if s.W.save_mode:
            img.save(f"out_{s.W.name}/network_{t}.png")
            
    def network_anim(s, animation_speed_inverse=10, detailed=0, state_variables="density_speed", minwidth=0.5, maxwidth=12, left_handed=1, figsize=(6,6), node_size=2, network_font_size=0, timestep_skip=24, file_name=None, legend=True):
        """
        Generates an animation of the entire transportation network and its traffic states over time.

        Parameters
        ----------
        animation_speed_inverse : int, optional
            The inverse of the animation speed. A higher value will result in a slower animation. Default is 10.
        detailed : int, optional
            Determines the level of detail in the animation.
            If set to 1, the link internals (cell) are displayed in detail.
            Under some conditions, the detailed mode will produce inappropriate visualization.
            If set to 0, the visualization is simplified to link-level. Default is 0.
        state_variables : str, optional
            Traffic state variables to be visualized. Default is "density_speed".
            The other option is "flow_delay". Anything other than "density_speed" is considered as "flow_delay" mode.
        minwidth : float, optional
            The minimum width of the link visualization in the animation. Default is 0.5.
        maxwidth : float, optional
            The maximum width of the link visualization in the animation. Default is 12.
        left_handed : int, optional
            If set to 1, the left-handed traffic system (e.g., Japan, UK) is used. If set to 0, the right-handed one is used. Default is 1.
        figsize : tuple of int, optional
            The size of the figures in the animation. Default is (6, 6).
        node_size : int, optional
            The size of the nodes in the animation. Default is 2.
        network_font_size : int, optional
            The font size for the network labels in the animation. Default is 20.
        timestep_skip : int, optional
            How many timesteps are skipped per frame. Large value means coarse and lightweight animation. Default is 8.
        file_name : str, optional
            The name of the file to which the animation is saved. It overrides the defauld name. Default is None.
        legend : bool, optional
            If set to True, the legend will be displayed. Default is True.  

        Notes
        -----
        This method generates an animation visualizing the entire transportation network and its traffic conditions over time.
        The animation provides information on vehicle density, velocity, link names, node locations, and more.
        The generated animation is saved to the directory `out<W.name>` with a filename based on the `detailed` parameter.

        Temporary images used to create the animation are removed after the animation is generated.
        
        In the default mode (`state_variables="density_speed"`), the color of the links represents the traffic speed (lighter colors indicate higher speeds), and the width of the links represents the traffic density (thicker links indicate higher densities).Although this combination of density and speed is intuitive, they are strongly correlated, so it is not very informative. Thus alternatively, with `state_variables="flow_delay"` mode, the color of the links represents the traffic speed (lighter colors indicate higher speeds), and the width of the links represents the traffic flow (thicker links indicate higher flows).
        Specific meaning of the colors (truncated "jet" colormap):

        - dark blue: free-flow (delay=free_flow_speed/speed-1 < 10%)
        - red: very congested (delay > 90%)
        """
        print(" generating animation...")
        pics = []
        for t in tqdm(range(0, int(s.W.TMAX), int(s.W.DELTAT*timestep_skip)), disable=False):
            img_ret = s.network(int(t), state_variables=state_variables, minwidth=minwidth, maxwidth=maxwidth, left_handed=left_handed, tmp_anim=1, figsize=figsize, node_size=node_size, network_font_size=network_font_size, image_return=True, legend=legend)
            pics.append(img_ret)
                
        fname = f"out_{s.W.name}/anim_network.gif"
        if file_name != None:
            fname = file_name
        pics[0].save(fname, save_all=True, append_images=pics[1:], optimize=False, duration=animation_speed_inverse*timestep_skip, loop=0)
        for f in glob.glob(f"out_{s.W.name}/tmp_anim_*.png"):
            os.remove(f)
        
    def network_fancy(s, animation_speed_inverse=10, figsize=5, sample_ratio=0.3, interval=3, network_font_size=0, trace_length=5, speed_coef=2, file_name=None, antialiasing=False):
        """
        Generates a visually appealing animation of vehicles' trajectories across the entire transportation network over time.

        Parameters
        ----------
        animation_speed_inverse : int, optional
            The inverse of the animation speed. A higher value will result in a slower animation. Default is 10.
        figsize : int or tuple of int, optional
            The size of the figures in the animation. Default is 6.
        sample_ratio : float, optional
            The fraction of vehicles to be visualized. Default is 0.3.
        interval : int, optional
            The interval at which vehicle positions are sampled. Default is 5.
        network_font_size : int, optional
            The font size for the network labels in the animation. Default is 0.
        trace_length : int, optional
            The length of the vehicles' trajectory trails in the animation. Default is 3.
        speed_coef : int, optional
            A coefficient that adjusts the animation speed. Default is 2.
        file_name : str, optional
            The name of the file to which the animation is saved. It overrides the defauld name. Default is None.
        antialiasing : bool, optional
            If set to True, antialiasing is applied to the animation. Default is True.

        Notes
        -----
        This method generates a visually appealing animation that visualizes vehicles' trajectories across the transportation network over time.
        The animation provides information on vehicle positions, speeds, link names, node locations, and more, with Bezier curves used for smooth transitions.
        The generated animation is saved to the directory `out<W.name>` with a filename `anim_network_fancy.gif`.

        Temporary images used to create the animation are removed after the animation is generated.
        """
        print(" generating animation...")

        # ベジエ補間
        from scipy.interpolate import make_interp_spline

        #{t: ["xs":[], "ys":[], "v": v, "c":c]}
        draw_dict = ddict(lambda: [])

        maxx = max([n.x for n in s.W.NODES])
        minx = min([n.x for n in s.W.NODES])
        dcoef = (maxx-minx)/20

        for veh in s.W.VEHICLES:
            if random.random() > sample_ratio:
                continue
            ts = []
            xs = []
            ys = []
            vs = []
            dx = (random.random()-0.5)*dcoef
            dy = (random.random()-0.5)*dcoef
            for i in range(0, len(veh.log_t), interval):
                if veh.log_state[i] in ["run", 2]:
                    link = s.W.LINKS[veh.log_link[i]]
                    x0 = link.start_node.x+dx
                    y0 = link.start_node.y+dy
                    x1 = link.end_node.x+dx
                    y1 = link.end_node.y+dy
                    alpha = veh.log_x[i]/link.length
                    ts.append(veh.log_t[i])
                    xs.append(x0*(1-alpha)+x1*alpha)
                    ys.append(y0*(1-alpha)+y1*alpha)
            for i in range(0, len(veh.log_t)):
                if veh.log_state[i] in ["run", 2]:
                    vs.append(veh.log_v[i]/s.W.LINKS[veh.log_link[i]].u)
            if len(ts) <= interval:
                continue

            # 点列
            points = np.array([xs, ys]).T

            # x, y 座標を取得
            x = points[:, 0]
            y = points[:, 1]

            # ベジエ曲線による補間
            t = np.linspace(0, 1, len(points))
            interp_size = len(ts)*interval
            t_smooth = np.linspace(0, 1, interp_size)
            bezier_spline = make_interp_spline(t, points, k=3)
            smooth_points = bezier_spline(t_smooth)
            for i in lange(t_smooth):
                ii = max(0, i-trace_length)
                if i < len(vs):
                    v = vs[i]
                else:
                    v = vs[-1]
                draw_dict[int(ts[0]+i*s.W.DELTAT)].append({
                    "xs": smooth_points[ii:i+1, 0],
                    "ys": smooth_points[ii:i+1, 1],
                    "c": gen_unique_color(veh.id, rgb_tuple=True),
                    "v": v
                })

        # 可視化
        maxx = max([n.x for n in s.W.NODES])
        minx = min([n.x for n in s.W.NODES])
        maxy = max([n.y for n in s.W.NODES])
        miny = min([n.y for n in s.W.NODES])

        if antialiasing:
            scale = 2
        else:
            scale = 1
        try:
            coef = figsize*100*scale/(maxx-minx)
        except:
            coef = figsize[0]*100*scale/(maxx-minx)
        maxx *= coef
        minx *= coef
        maxy *= coef
        miny *= coef

        buffer = (maxx-minx)/10
        maxx += buffer
        minx -= buffer
        maxy += buffer
        miny -= buffer

        pics = []
        for t in tqdm(range(int(s.W.TMAX*0), int(s.W.TMAX*1), int(s.W.DELTAT*speed_coef))):
            img = Image.new("RGBA", (int(maxx-minx), int(maxy-miny)), (255, 255, 255, 255))
            draw = ImageDraw.Draw(img)
                
            if network_font_size > 0:
                font = ImageFont.load_default(size=30)

            def flip(y):
                return img.size[1]-y

            for l in s.W.LINKS:
                x1, y1 = l.start_node.x*coef-minx, l.start_node.y*coef-miny
                x2, y2 = l.end_node.x*coef-minx, l.end_node.y*coef-miny
                n_lane = 1#l.number_of_lanes
                draw.line([(x1, flip(y1)), (x2, flip(y2))], fill=(200,200,200), width=int(n_lane*scale), joint="curve")

                if network_font_size > 0:
                    draw.text(((x1+x2)/2, flip((y1+y2)/2)), l.name, font=font, fill="blue", anchor="mm")

            traces = draw_dict[t]
            for trace in traces:
                xs = trace["xs"]*coef-minx
                ys = trace["ys"]*coef-miny
                size = 1.5*(1-trace["v"])*scale
                coords = [(l[0], flip(l[1])) for l in list(np.vstack([xs, ys]).T)]
                try:
                    draw.line(coords,
                            fill=(int(trace["c"][0]), int(trace["c"][1]), int(trace["c"][2])), width=scale, joint="curve")
                    draw.ellipse((xs[-1]-size, flip(ys[-1])-size, xs[-1]+size, flip(ys[-1])+size), 
                            fill=(int(trace["c"][0]), int(trace["c"][1]), int(trace["c"][2])))
                except Exception as e:
                    warnings.warn(str(e))

                #draw.line([(x1, flip(y1)), (xmid1, flip(ymid1)), (xmid2, flip(ymid2)), (x2, flip(y2))]

            font = ImageFont.load_default(size=30)
            draw.text((img.size[0]/2,20), f"t = {t :>8} (s)", font=font, fill="black", anchor="mm")

            if antialiasing:
                img = img.resize((int((maxx-minx)/scale), int((maxy-miny)/scale)), resample=Resampling.LANCZOS)
                
            byte_stream = io.BytesIO()
            img.save(byte_stream, format='PNG')
            byte_stream.seek(0)
            pics.append(Image.open(byte_stream))

            #img.save(f"out_{s.W.name}/tmp_anim_{t}.png")
            #pics.append(Image.open(f"out_{s.W.name}/tmp_anim_{t}.png"))

        fname = f"out_{s.W.name}/anim_network_fancy.gif"
        if file_name != None:
            fname = file_name
        pics[0].save(fname, save_all=True, append_images=pics[1:], optimize=False, duration=animation_speed_inverse*speed_coef, loop=0)

        return pics[int(len(pics)/2)]

    def df_vehicle_details(s, idx):
        veh = s.W.VEHICLES[idx]
        df = pd.DataFrame({
            "id": [veh.id for _ in veh.log_t],
            "t": veh.log_t,
            "orig": [veh.orig.name for _ in veh.log_t],
            "dest": [veh.dest.name for _ in veh.log_t],
            "state": [dict_VehicleState[elem] for elem in veh.log_state],
            "link": [s.W.LINKS[elem].name if elem != -1 else "-1" for elem in veh.log_link],
            "x": veh.log_x,
            "v": veh.log_v,
        })

        return df

    def df_vehicles(s):
        df = pd.DataFrame({
            "id": [veh.id for veh in s.W.VEHICLES],
            "orig": [veh.orig.name for veh in s.W.VEHICLES],
            "dest": [veh.dest.name for veh in s.W.VEHICLES],
            "final_state": [dict_VehicleState[veh.log_state[-1]] for veh in s.W.VEHICLES],
            "departure_time": [veh.departure_time for veh in s.W.VEHICLES],
            "arrival_time": [veh.arrival_time for veh in s.W.VEHICLES],
            "travel_time": [veh.arrival_time-veh.departure_time if veh.arrival_time>0 else -1 for veh in s.W.VEHICLES],
            "distance_traveled": [-1 for veh in s.W.VEHICLES], #TODO: implement calculation in C++
            "average_speed": [-1 for veh in s.W.VEHICLES],#TODO: implement calculation in C++
        })

        return df
    
    def df_link_details(s, link):        
        if isinstance(link, str):
            link = s.W.get_link(link)
        else:
            link = s.W.LINKS[int(link)]

        df = pd.DataFrame({
            "name": [link.name for _ in range(len(link.arrival_curve))],
            "t": [t*s.W.DELTAT for t in range(len(link.arrival_curve))],
            "cumulative_arrivals": link.arrival_curve,
            "cumulative_departures": link.departure_curve,
            "number_of_vehicles": np.array(link.arrival_curve)-np.array(link.departure_curve),
            "average_speed": link.length/np.array(link.traveltime_instant),
            "travel_time": link.traveltime_real,
        })

        return df
    
    def df_links(s):
        df = pd.DataFrame({
            "name": [link.name for link in s.W.LINKS],
            "start_node": [link.start_node.name for link in s.W.LINKS],
            "end_node": [link.end_node.name for link in s.W.LINKS],
            "length": [link.length for link in s.W.LINKS],
            "traffic_volume": [link.cum_departure[-1] for link in s.W.LINKS],
            "vehicles_remain": [link.cum_arrival[-1]-link.cum_departure[-1] for link in s.W.LINKS],
            "free_travel_time": [link.length/link.u for link in s.W.LINKS],
            "average_travel_time": [np.average(link.traveltime_real) for link in s.W.LINKS],
            "stddiv_travel_time": [np.std(link.traveltime_real) for link in s.W.LINKS],
        })

        return df
