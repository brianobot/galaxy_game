# this functions allows for linear transformation between the default 2D plane with normal x and y
# axis to a perspective plane..the details in the computation is explained in my perspective tutorials
# https://www.learn_well.com/perspective_transformations.html

def transform(self, x, y):
        # return self.transform_2D(x, y)
        return self.transform_Perspective(x, y)

def transform_2D(self, x, y):
    return int(x), int(y)

def transform_Perspective(self, x, y):
    lin_y = y * self.perspective_point_y /self.height
    if lin_y > self.perspective_point_y:
        lin_y = self.perspective_point_y 

    diff_x = x - self.perspective_point_x
    diff_y = self.perspective_point_y - lin_y
    factor_y = diff_y/self.perspective_point_y
    factor_y *= factor_y

    tr_x = self.perspective_point_x + diff_x*factor_y 
    tr_y = self.perspective_point_y - factor_y*self.perspective_point_y
    return int(tr_x), int(tr_y) 
