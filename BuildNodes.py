import os,sys
import numpy as np
import matplotlib.pyplot as plt
import datetime
import glob
import pandas as pd


# results = df.groupby(["x", "y"]).size()                                 
# results = results[results > 1]
# print("Len of duplicates:",len(results))
class fovpoint:
    def __init__(self,point=None,R=0.02): # R=0.02
        self.point = point
        self.R = R
        self.dPhi = point.dPhi / 2
        self.direction = point.direction

    def distance(self,p):
        return np.sqrt((p.x - self.point.x)**2 + (p.y - self.point.y)**2)
    def angle_between(self,p):
        return np.arctan2(p.x - self.point.x, p.y - self.point.y) * (180 / np.pi)
    
    # def adjust_bearing(self,angle):
    #     if angle>=0 and angle < 180:
    #         #print("proccing between 0-180")
    #         nangle = angle + 180
    #         return nangle
    #     elif angle>=180 and angle <= 360:
    #         #print("proccing between 180-360")
    #         nangle = angle - 180
    #         return nangle
    #     else:
    #         print("something is wrong, check angle")

    @staticmethod
    def adjust_bearing(angle):
        if angle>=0 and angle < 180:
            #print("proccing between 0-180")
            nangle = angle + 180
            return nangle
        elif angle>=180 and angle <= 360:
            #print("proccing between 180-360")
            nangle = angle - 180
            return nangle
        else:
            print("something is wrong, check angle")
            
            
    def angles(self,p,angle):
        angle_p1_p2 = self.angle_between(p)
        angle_diff = np.abs(angle - angle_p1_p2)
        return angle_diff
        

    def special_case(self,p):
        #if points are on top of each other within fov will fail, so we perform special case
        if self.point.direction == 2 and p.direction==1:
            return True
        elif self.point.direction == 3:
            return True
        else:
            return False


        
    def within_field_of_view(self, p):
        # 0: None | 1: away | 2: toward | 3: both
        self.dist = self.distance(p)
        if (self.point.x == p.x) and (self.point.y == p.y):
            tmp = self.special_case(p)
            return tmp
        #direction = self.point.direction
        if self.direction==1:
            angle_diff = self.angles(p,self.point.bearing)
            return self.dist <= self.R and angle_diff <= self.dPhi #angle_tolerance
        elif self.direction==2:
            adjusted=self.adjust_bearing(self.point.bearing)
            angle_diff = self.angles(p,adjusted)

            return self.dist <= self.R and angle_diff <= self.dPhi #angle_tolerance
        elif self.direction==3:
            angle_diff1 = self.angles(p,self.point.bearing)
            angle_diff2 = self.angles(p,self.adjust_bearing(self.point.bearing))
            
            mask1 = self.dist <= self.R and angle_diff1 <= self.dPhi
            mask2 = self.dist <= self.R and angle_diff2 <= self.dPhi
            return any((mask1,mask2))
        
    def draw_cone(self,ax,plabel="point",color="green"):

        if self.direction == 1:
            angle_rad_list = [np.deg2rad(self.point.bearing)]
        elif self.direction == 2:
            angle_rad_list = [np.deg2rad(self.adjust_bearing(self.point.bearing))]
        elif self.direction == 3:
            angle_rad_list = [np.deg2rad(self.point.bearing),
                         np.deg2rad(self.adjust_bearing(self.point.bearing))
                         ]
        for angle_rad in angle_rad_list:
            view_cone_x = [self.point.x, self.point.x + self.R * np.sin(angle_rad + np.deg2rad(self.dPhi)), 
                        self.point.x + self.R * np.sin(angle_rad - np.deg2rad(self.dPhi)), self.point.x]
            view_cone_y = [self.point.y, self.point.y + self.R * np.cos(angle_rad + np.deg2rad(self.dPhi)), 
                        self.point.y + self.R * np.cos(angle_rad - np.deg2rad(self.dPhi)), self.point.y]
            ax.plot(view_cone_x, view_cone_y, '-',color=color, label=f'{plabel} view cone',alpha=0.5)


def main():
    data = "../gps_data/CamerasForUse_Modified.csv"
    df = pd.read_csv(data,header=0)
    df["direction"] = df["direction"].astype(int)

    p1,p2 = df.iloc[0,:],df.iloc[2,:]
    p3= pd.DataFrame({"x":[p1.x + 0.01],"y":[p1.y]}).iloc[0,:]
    
    point = fovpoint(p1)
    fFov = point.within_field_of_view(p3)

    # Plotting
    fig, ax = plt.subplots(figsize=(8,6))

    # Plot points
    ax.plot(p1.x, p1.y, 'ro', label='p1')
    ax.plot(p2.x, p2.y, 'bo', label='p2')
    ax.plot(p3.x, p3.y, 'gd', label='p3')

   
    # Set axis labels
    ax.set_xlabel('x')
    ax.set_ylabel('y')

    # Set title
    ax.set_title('Field of View')

    # Add legend
    ax.set_xlim(11.97,12)
    ax.set_ylim(57.68,57.72)

    # Show plot
    plt.grid()
    plt.show()

if __name__=="__main__":
    main()
