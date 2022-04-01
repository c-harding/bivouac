import numpy as np
import math
from elevation import getElevationMatrix, rasterToImage, getRasterRGB
from local_config import MAPBOX_TOKEN
import mercantile
import basic_weather_calls

def wind_shelter_prep(radius,direction,tolerance):
    nc = 2*int(radius)+1
    nr=nc
    mask=np.ones((nc,nr),dtype=np.int8)
    for j in range(nc):
        for i in range(nr):
            if i==j and i==((nr+1)/2):
                continue
            xy = [j-(nc+1)/2, (nr+1)/2-i]
            xy = xy / np.sqrt(xy[0]**2+xy[1]**2)
            if ( xy[1]>0):
                a = np.arcsin(xy[0])  
            else:
                a = np.pi - np.arcsin(xy[0])
            if (a < 0):
                a = a + 2*np.pi
            d = abs(direction-a)
            if (d>2*np.pi):
                d = d-2*np.pi
            d = min(d,2*np.pi-d)
            if (d<=tolerance):
                mask[i,j] = 0
    
    

    return mask


def centervalue(x): 
    i = math.ceil(x.shape[1] / 2)
    return(x[i,i],i)  

def shelter_index(x,mask,radius,cellsize):
    
    ctr,coord_x = centervalue(x)
    x = x[coord_x-radius:coord_x+1+radius,coord_x-radius:coord_x+1+radius]

    ctr_c,coord_c = centervalue(mask)
    
    for i in range(x.shape[0]):
        for j in range(x.shape[1]):
            if mask[i,j]==1:
               
                x[i,j] = np.nan
    
    res = np.nan
    x_list =[]
    for i in range(x.shape[0]):
        for j in range(x.shape[1]):
            if not np.isnan(x[i,j]):
                point_coords = (i,j)
                if point_coords != (coord_c,coord_c):
                    distance = np.sqrt((coord_c-point_coords[0])**2+(coord_c-point_coords[1])**2) * cellsize
                    x_list.append(np.arctan((x[point_coords[0],point_coords[1]]-ctr)/distance))
           
    res = max(x_list)
    
    
    return(res)


def shelter_index_non_centre(x,mask,radius,cellsize,coord_x,coord_y):
    
    
    x = x[coord_x-radius:coord_x+1+radius,coord_y-radius:coord_y+1+radius]

    ctr_c,coord_c = centervalue(mask)
    
    for i in range(x.shape[0]):
        for j in range(x.shape[1]):
            if mask[i,j]==1:
               
                x[i,j] = np.nan
    
    res = np.nan
    x_list =[]
    
    ctr = x[coord_c,coord_c]
    for i in range(x.shape[0]):
        for j in range(x.shape[1]):
            if not np.isnan(x[i,j]):
                point_coords = (i,j)
                if point_coords != (coord_c,coord_c):
                    distance = np.sqrt((coord_c-point_coords[0])**2+(coord_c-point_coords[1])**2) * cellsize
                    x_list.append(np.arctan((x[point_coords[0],point_coords[1]]-ctr)/distance))
           
    res = max(x_list)
    
    
    return(res)


def wind_shelter(lat,long,zoom):
    #creating elevation matrix
    tile_coords = mercantile.tile(lng, lat, zoom)
    elevation_mat = getElevationMatrix(MAPBOX_TOKEN, tile_coords.z, tile_coords.x, tile_coords.y)    

    #finding wind direction at coords
    direction = np.pi/180*basic_weather_calls.wind_direction(lat,lng)
    
    print(direction)
    
    #initial values
    
    tolerance = 30*np.pi/180 #from first paper
    
    #calculation of cellsize
    latitude_radians = lat * math.pi / 180
    
    cellsize = abs(156543.03 * np.cos(latitude_radians) / (2 ** zoom))
    
    
    #using a max dist of 100m (from paper), calculating radius by zoom
    radius = math.ceil(100/cellsize)
    
    #creating mask for windward direction
    mask = wind_shelter_prep(radius,direction,tolerance)
    
    #calculating wind shelter
    shelter = shelter_index(elevation_mat,mask,radius,cellsize)
    
    return shelter
    
    
    
    
    
#usage   
    
    
lng=45.558726
lat=6.715438
zoom = 14

shelter = wind_shelter(lat,lng,zoom)
print(shelter)