$fn=30;

//bat();

h=6;
w=34;
l=51;

module bat()color([1,0,0])cube([l,w,h]);



difference() {
  union() {
    hull(){
      translate([-5,6,0])cylinder(r=5,h=h+2);
      translate([-5,w-6,0])cylinder(r=5,h=h+2);
      translate([l+5,6,0])cylinder(r=5,h=h+2);
      translate([l+5,w-6,0])cylinder(r=5,h=h+2);
    }
  }
  hull(){
    translate([8,10,0])cylinder(r=5,h=h+4);
    translate([8,w-10,0])cylinder(r=5,h=h+4);
    translate([l-8,10,0])cylinder(r=5,h=h+4);
    translate([l-8,w-10,0])cylinder(r=5,h=h+4);
  }
  translate([0,w/2,h/2])cube([40,10,h*22], center=true);

  translate([-5,6,-1])cylinder(r=3.5/2,h=h+4);
  translate([-5,w-6,-1])cylinder(r=3.5/2,h=h+4);
  translate([l+5,6,-1])cylinder(r=3.5/2,h=h+4);
  translate([l+5,w-6,-1])cylinder(r=3.5/2,h=h+4);
  
  bat();
}