# Flash-Skeleton
Flash Skeleton is a Python script that helps with converting Flash Applications to Web Applications by generating an application skeleton using cv2, automatically extracting and sizing assets. Some of it is specific to the work done for read-write-think.
## Useful For
* Application pages with many assets and packed-together elements
* Framing pages with many buttons and inputs
## What it Does
* Collects assets for backgrounds and buttons (including hover versions) and automatically sizes them.
* Creates a .html and .css (with accompanying .scss) file to serve as an outline of the application page, including the buttons and inputs collected from user input.
## Dependencies
* pillow
* cv2
* pynput
* numpy
* pyautogui
Note: There may be limitations for pynput if you are on Linux or MacOS (see [here](https://pynput.readthedocs.io/en/latest/limitations.html) for more details.)
 ## Set Up (Per Application)
 1. At the top of the python file, edit the last folder in the `assetsDirectory` path string to reflect the name of your app (e.g. `/assets/persuasion-map`.)
 2. Edit the `imagePrefix` variable to give all your asset names a common beginning (Angular gets confused if assets between components have the same name so this tries to prevent that.) I prefer to make it two letters followed by a dash, e.g. `pm-` for the app Persuasion Map.
 3. Choose RGB values for the arrays `buttonRGB` and `inputRGB` for asset scraping. Try to make them colors that will not appear in your app. You will see what these do later.
 4. Enter the target dimensions for your web app in `backgroundDimensions` (width, height).
 5. Now, for `backgroundCoordinates`, you will get the pixel coordinates of the corners of the Flash app. One way to do this to take a screenshot of the app (it is better to do this in fullscreen - but if not, keep it consistent.) Then open the image in your favorite image editor (I use [paint.net](https://www.getpaint.net/).) Get the pixel coordinates for the top left corner of the app area you wish to scrape, and place them in the first two values of `backgroundCoordinates` (width, height). Do the same with the bottom right corner, placing them in the next two values of `backgroundCoordinates`. Note that you should add one to each of the values for this corner to make sure you scrape everything.
## Workflow
Let's say you have an application page with multiple buttons, inputs, or both. This script will assist you in replicating it. You may not necessarily save much time, but hey, it won't be quite as laborious.

1. The way that the script determines element locations is by the coordinates of rectangles, and you must provide these rectangles to the script. Create a directory for the application page with whatever name you choose. Put it in the same folder as the script.
2. Take a screenshot of the application page (make sure it is in the same way as when you got the background coordinates.) Open this up in an image editor.
3. You may skip this step if there are no buttons on the page. Refer back to the RGB values you chose for `buttonRGB`, and place solid rectangles of that color on top of the buttons you wish to replicate. Note that the script will not work if this color already appears somewhere on the page. Save this as `button-template.png` in the directory you created earlier.
4. You may skip this step if there are no text inputs on the page. If you already created a button template, be sure you are using a fresh screenshot in your editor. Refer back to the RGB values you chose for `inputRGB`, and place solid rectangles of that color on top of the inputs you wish to replicate. Note that the script will not work if this color already appears somewhere on the page. Save this as `input-template.png` in the directory you created earlier.
5. Run the script, and enter the name of the directory you created. Return to the application, and press `[` to begin scraping. The background will be scraped (note that since element positioning is pixel-perfect, there is no need to remove them in the background image,) and then your mouse will move to the center of each button to scrape its hover asset. If something has gone wrong, you may press `]` at any time to stop the script.
6. The script will open a picture of each button and ask you to enter a name for it. This can be whatever you wish.
7. The script will then ask you to enter a name for each of the text inputs in the order of top to bottom, left to right. You can enter anything. It will also ask you whether it is an `input` element (one-line) or a `textarea` element (multi-line,) to which you can answer `i` for `input` or `t` for `textarea`.
8. You can now check the directory you created earlier. There should be a .html, .css. and .scss file. You may open the .html to make sure the page looks how you want. Since you are viewing it outside the development environment, there are some default browser stylings that will make the page on the .html file look awful, so add the provided `reset.css` file to the directory to make it look as it should (it is already linked in the html.) This can be skipped if you are confident that the result is what you want (it should be if done correctly.)
9. Once you are happy with your result, you can easily migrate the page to your component. Move the assets into your component's asset directory, and copy the html/scss from the relevant files. Congratulations! You have now replicated the application page in the most convoluted way possible.

Note 1: Each of the elements have the styling `position: absolute`. This is admittedly different from how the apps are often made, but it makes it much easier to treat each element independently. It also does not prevent elements with relative positioning from being added. 

Note 2: Backgrounds will automatically have the class `frame`. By default, `frame` will have `width` and `height` attributes corresponding to the target dimensions, as well as `position: relative`, but you may change this as you see fit.

Note 3: Because the app assets are already stored in the `/assets/[app-name]` directory structure, paths in the files do not need to be changed.

Note 4: The scaling factor for both width and height are printed at the beginning of each use (`xSizingScaleFactor` and `ySizingScaleFactor`.) This will make any manual sizing easier.

Let me know if there are any questions or if you have an issue with the script. I personally find it helpful, but depending on your workflow, you may not.
