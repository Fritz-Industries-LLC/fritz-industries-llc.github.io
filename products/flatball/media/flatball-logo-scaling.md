
./flatball-logo.png has a circle surrounding a logo / badge.

i have measured the location of the left-most point on the circle at:
- ~355,485px
and the right-most point on the circle at:
- ~1175,485px

or ~820px diameter.

can you generate the same image scaled so the circle has a 135mm diameter
and the image is at 600dpi?

also, id like this to be in landscape orientation and for there to be a
ruler with major ticks at 1cm and minor ticks at 1mm along the left side
of the image.  the ruler should be set back from the circle by 75mm

8.5in	--> 215.9mm
11in	--> 279.4mm
5.5in	--> 139.7mm		--> 135mm
6.6in	--> 167.6mm		--> 165mm

py .\flatball-logo-scale-with-ruler.py --help

py .\flatball-logo-scale-with-ruler.py --input flatball-logo.png --output flatball-logo-with-ruler.png --dpi 600 --circle-left-x 355 --circle-right-x 1175 --target-circle-diameter 135 --ruler-setback 75 --paper-size ansi.a --orientation landscape

py .\flatball-logo-scale-with-ruler.py --input flatball-logo.png --output flatball-logo-with-ruler.png --dpi 600 --circle-left-x 355 --circle-right-x 1535 --target-circle-diameter 135 --ruler-setback 75 --paper-size ansi-a --orientation landscape

lets switch from:
--circle-left-x 355 --circle-right-x 1175 --target-circle-diameter 135
to say:
--image-center-x 500 --image-center-y 500 --target-image-diameter 135

py .\flatball-logo-scale-with-ruler.py --input flatball-logo.png --output flatball-logo-with-ruler.png --dpi 600 --image-center-x-px 765 --image-center-y-px 485 --image-diameter-px 820 --target-image-diameter-mm 135 --ruler-setback 75 --paper-size ansi-a --orientation landscape

py .\flatball-logo-scale-with-ruler.py --input flatball-logo.png --output flatball-logo-with-ruler.png --dpi 600 --image-center-x-px 765 --image-center-y-px 485 --image-diameter-px 820 --target-image-diameter-mm 135 --paper-size ansi-a --orientation landscape --ruler-setback-mm 25

py .\flatball-logo-scale-with-ruler.py --input flatball-logo.png --output flatball-logo-with-ruler.png --dpi 600 --image-center-x-px 750 --image-center-y-px 500 --image-diameter-px 820 --target-image-diameter-mm 135 --paper-size ansi-a --orientation landscape --ruler-setback-mm 25

py .\flatball-logo-scale-with-ruler.py --input flatball-logo.png --output flatball-logo-with-ruler.png --dpi 600 --image-center-x-px 765 --image-center-y-px 480 --image-diameter-px 810 --target-image-diameter-mm 135 --paper-size ansi-a --orientation landscape --ruler-setback-mm 25

py .\flatball-logo-scale-with-ruler.py --input flatball-logo.png --output flatball-logo-with-ruler.png --dpi 600 --image-center-x-px 765 --image-center-y-px 480 --image-diameter-px 810 --target-image-diameter-mm 135 --paper-size ansi-a --orientation landscape --ruler-margins-mm 25

py .\flatball-logo-scale-with-ruler.py --input flatball-logo.png --output flatball-logo-with-ruler.png --dpi 600 --image-center-x-px 765 --image-center-y-px 480 --image-diameter-px 810 --target-image-diameter-mm 165 --paper-size ansi-a --orientation landscape --ruler-margins-mm 25
