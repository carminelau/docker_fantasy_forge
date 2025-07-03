import trimesh
import pyvista as pv
import numpy as np
import os
from moviepy import ImageSequenceClip
import tqdm
import requests

def load_stl(file_path):
    mesh = trimesh.load(file_path)
    return mesh

def generate_images(mesh, num_frames=60, output_folder='frames'):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    light = pv.Light(position=(1, 1, 1), color='white')
    light.positional = True
    
    angles = np.linspace(0, 360, num_frames)
    
    for i, angle in enumerate(angles):
        plotter = pv.Plotter(off_screen=True)
        pv_mesh = pv.wrap(mesh)
        plotter.add_mesh(pv_mesh, specular=1.0, diffuse=0.7, smooth_shading=True)
        plotter.camera_position = 'iso'
        plotter.camera.azimuth = angle
        frame_path = os.path.join(output_folder, f'frame_{i:04d}.png')
        plotter.show(screenshot=frame_path)
                # Close the plotter to release resources
        plotter.close()
        
def create_video(output_folder='frames', video_file='output_video.mp4', fps=30):
    frame_files = sorted([
        os.path.join(output_folder, f) for f in os.listdir(output_folder) if f.endswith('.png')
    ])
    
    clip = ImageSequenceClip(frame_files, fps=fps)
    clip.write_videofile(video_file, codec='libx264')
    with open(f"{video_file}", 'rb') as video_file_open:
        file = {'file': video_file_open}
        datas = {'filename' : video_file.split("\\")[1]}
        print(f'Caricamento del file {video_file.split("\\")[1]} su MongoDB...')
        file_id  = requests.post("http://193.205.184.149:5000/add_file", files=file, data=datas)    
        print(f'Caricato {video_file.split("\\")[1]} con ID {file_id}')


lista_dir_classi = os.listdir("C:\\Users\\Admin\\OneDrive\\File 3D\\Catalogo miniature")
print(f"Numero di Classi directory trovate: {len(lista_dir_classi)}")
miniatures = []

lista_dir_classi = ["speciale-X013", "warlock-X012"]
for d_classe in lista_dir_classi:
    lista_dir_min = os.listdir(f"C:\\Users\\Admin\\OneDrive\\File 3D\\Catalogo miniature\\{d_classe}")
    #print(f"Numero di cartelle trovate nella classe {d_classe}: {len(lista_dir_min)}")

    for d_min in lista_dir_min:
        lista_file = os.listdir(f"C:\\Users\\Admin\\OneDrive\\File 3D\\Catalogo miniature\\{d_classe}\\{d_min}")
        print (lista_file)
        #print(f"Numero di file STL trovati nella cartella {d_min}: {len(lista_file)}")

        for file in lista_file:
            if file.endswith('.stl'):
                miniatures.append(f"C:\\Users\\Admin\\OneDrive\\File 3D\\Catalogo miniature\\{d_classe}\\{d_min}\\{file}")
print(f"Numero di file STL trovati: {len(miniatures)}")

#mi crei una barra di progresso per vedere quanto tempo manca 
for i in tqdm.tqdm(range(len(miniatures)), desc="Processing STL files"):

    output_folder = 'frames'
    video_file = f'videos\\{miniatures[i].split("\\")[-1].split(".")[0]}.mp4'

    # Load the STL file
    mesh = load_stl(miniatures[i])

    # # Generate images
    generate_images(mesh, num_frames=60, output_folder=output_folder)

    # # Create the video
    create_video(output_folder=output_folder, video_file=video_file, fps=30)

    # Clean up frames after video creation
    for frame_file in os.listdir(output_folder):
        os.remove(os.path.join(output_folder, frame_file))