from vpython import sphere, vector, color, rate , mag , norm, scene , sqrt , label , slider , menu
import json
import os
G = 6.6743e-11 #gravity constant
AU = 1.496e11
COMPRESSION_FACTOR = 5000
dt = 360 #time diff
steps_per_frame = 100
current_focus = None  


class Planet:
    def __init__(self,pos,velocity,mass,visual,parent,name,label):
        self.pos = pos
        self.mass = mass
        self.visual = visual
        self.velocity = velocity
        self.acc = vector(0, 0, 0)
        self.parent = parent
        self.name = name
        self.label = label
        pass
def change_focus(event):
    global current_focus
    target = scene.mouse.pick
    if target != None:
        scene.camera.follow(target)
        for p in planets:
            if p.visual == target:
                current_focus = p
    else:
        scene.camera.follow(None)
        current_focus = None
def system_acceleration(planets):
    for p in planets:
        p.acc = vector(0, 0, 0)
    for i in range(len(planets)):
        for j in range(i+1,len(planets)):
            distance = planets[j].pos - planets[i].pos
            r = mag(distance)
            direction = norm(distance)
            acc_magn = G*planets[j].mass/(r*r)
            acc_velo = acc_magn*direction
            planets[i].acc = planets[i].acc + acc_velo
            acc_magn = G*planets[i].mass/(r*r)
            acc_velo = acc_magn*direction
            planets[j].acc = planets[j].acc - acc_velo
def adjust_speed(s):
    global steps_per_frame
    steps_per_frame = s.value
def choose_focus(m):
    global current_focus
    if m.selected == "None":
        scene.camera.follow(None)
        current_focus = None
    else:
        target_planet = planet_directory.get(m.selected)
        scene.camera.follow(target_planet.visual)
        current_focus = target_planet

script_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(script_dir, 'planets.json')
with open(json_path, 'r') as file:
    planet_dict = json.load(file)

planets = []
planet_directory = {}
for n in planet_dict:
    pos_vec = vector(n["distance"], 0, 0)
    vel_vec = vector(n["velocity"][0], n["velocity"][1], n["velocity"][2])
    if isinstance(n["color"],list):
        temp_color = color.gray(n["color"][1])
    else:
        temp_color = getattr(color,n["color"])
    visual = sphere(pos=vector(0, 0, 0), radius=n["radius"], color=temp_color ,make_trail=False, retain=30,)
    actual_parent = None
    if n["parent"] != None:
        actual_parent = planet_directory.get(n["parent"])
    is_vis = (n["parent"] == None or n["parent"] == "Sun")
    planet_label = (label(text=n["name"], box=False, height=10,visible = is_vis))
    temp_planet =(Planet(pos_vec, vel_vec, n["mass"], visual,actual_parent,n["name"],planet_label))
    planets.append(temp_planet)
    planet_directory[n["name"]] = temp_planet

scene.bind("mousedown",change_focus)
system_acceleration(planets)
scene.append_to_title('Simulation Speed: ')
choices_list = ["None"] + list(planet_directory.keys())
scene.append_to_title('   Camera Focus: ')
focus_menu = menu(choices=choices_list, bind=choose_focus)
scene.append_to_title('\n\n')
speed_slider = slider(pos=scene.title_anchor, bind=adjust_speed, min=1, max=100, value=10, length=400)
scene.append_to_title('\n\n')
while True:
    rate(144)
    for _ in range(int(steps_per_frame)):
        for p in planets:
            p.old_acc = p.acc
            p.pos = p.pos + p.velocity*dt + p.acc*dt*dt/2        
        system_acceleration(planets)

        for p in planets:
            p.velocity = p.velocity + (p.old_acc + p.acc)*dt/2
    for p in planets:
        if p.parent == None:
            p.visual.pos = vector(0, 0, 0)
        elif p.parent.name == "Sun":
             true_r = mag(p.pos)
             fake_r = sqrt(true_r) / COMPRESSION_FACTOR 
             p.visual.pos = norm(p.pos) * fake_r
        else:
            relative = p.pos - p.parent.pos
            relative_mag = p.parent.visual.radius + (sqrt(mag(relative)) / COMPRESSION_FACTOR)
            p.visual.pos = norm(relative) *relative_mag + p.parent.visual.pos
        #changing label y value
        p.label.pos = p.visual.pos - vector(0, p.visual.radius*1.5+0.5, 0)
        if p.parent == None:
            continue
        elif p.parent.name != "Sun":
            if current_focus == p.parent or current_focus == p:
                p.label.visible = True
            else: 
                p.label.visible = False

