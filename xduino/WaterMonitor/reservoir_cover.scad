flatten = 93.5;
$fn=45;

rotate([-flatten,0,0])it_with_holes();


module through(){
  cylinder(h=20,r=1, center=true);
}module through2()hull(){
  cylinder(h=20,r=1, center=true);
  translate([0,10,0])cylinder(h=20,r=1, center=true);
}

module it_with_holes()difference(){
  it();
  #translate([-18,0,0])rotate([90,0,0])through();
  #translate([18,0,0])rotate([90,0,0])through();
  #translate([-18,0,-24])rotate([90,0,0])through2();
  #translate([18,0,-24])rotate([90,0,0])through2();
  hull() {
    translate([7,-3,-17])rotate([flatten,0,0])cylinder(h=10,r=9.5, center=true);
    translate([-7,-3,-17])rotate([flatten,0,0])cylinder(h=10,r=9.5, center=true);
  }
}


module it()difference(){
  union(){
    rotate([90,0,0])hull() {
      translate([21.5,0,-2])cylinder(h=8, r=6.5);
      translate([-21.5,0,-2])cylinder(h=8, r=6.5);
    }

    hull() {
      translate([0,0,6])cube([42,4,1], center=true);
      translate([0,2,-27])cube([42,4,1], center=true);
    }
  }
 # translate([-40,0,6.5])rotate([70,0,0])translate([0,-2,-15])cube(80,40,40);
}