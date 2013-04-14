<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<title>Treemap - Animated Squarified, SliceAndDice and Strip TreeMaps</title>

<!-- CSS Files -->
<link type="text/css" href="./css/base.css" rel="stylesheet" />
<link type="text/css" href="./css/TreeMap.css" rel="stylesheet" />
<link type="text/css" href="./css/menue.css" rel="stylesheet" />

<!--[if IE]><script language="javascript" type="text/javascript" src="./Jit/Extras/excanvas.js"></script><![endif]-->

<!-- JIT Library File -->
<script language="javascript" type="text/javascript">
var labelType, useGradients, nativeTextSupport, animate;

(function() {
  var ua = navigator.userAgent,
      iStuff = ua.match(/iPhone/i) || ua.match(/iPad/i),
      typeOfCanvas = typeof HTMLCanvasElement,
      nativeCanvasSupport = (typeOfCanvas == 'object' || typeOfCanvas == 'function'),
      textSupport = nativeCanvasSupport 
        && (typeof document.createElement('canvas').getContext('2d').fillText == 'function');
  //I'm setting this based on the fact that ExCanvas provides text support for IE
  //and that as of today iPhone/iPad current text support is lame
  labelType = (!nativeCanvasSupport || (textSupport && !iStuff))? 'Native' : 'HTML';
  nativeTextSupport = labelType == 'Native';
  useGradients = nativeCanvasSupport;
  animate = !(iStuff || !nativeCanvasSupport);
})();

var Log = {
  elem: false,
  write: function(text){
    if (!this.elem) 
      this.elem = document.getElementById('log');
    this.elem.innerHTML = text;
    this.elem.style.left = (500 - this.elem.offsetWidth / 2) + 'px';
  }
};


function displayTreemap(view){
  //init data
  var json
  if( view == "files_view"){
	json = ${filesize_treemap}
  }
  if( view == "git_view"){
	json = ${git_treemap}
  }
  if( view == "author_view"){
	json = ${authors_treemap}
	document.getElementById("dropdown_authors").style.visibility="visible"
    dd_authors = document.getElementById("dropdown_authors")
    author = dd_authors.options[dd_authors.selectedIndex].value
	json = json[author] 
  } else {
	document.getElementById("dropdown_authors").style.visibility="hidden"
  }
  
  

  selectedView = document.getElementById('selected_view');
  if( view=='git_view'){
    selectedView.setAttribute('src', './img/git_button.png');
  }
  if( view=='files_view'){
    selectedView.setAttribute('src', './img/files_button.png');
  }
  if( view=='author_view'){
    selectedView.setAttribute('src', './img/author_button.png');
  }
	

  function tooltip(tip, node, isLeaf, domElement) {  
		packagetxt = ""
        var data = node.data;
		if( data.isPackage ) {
			packagetxt = "package: "
		}
        var html = "<div class=\"tip-title\">" + packagetxt + node.name 
          + "</div><div class=\"tip-text\">";
          
        if(data.hash) {
          html += "hash: " + data.hash+"<br/>";
        }
        if(data.date) {
          html += "date: " + data.date+"<br/>";
        }
        if(data.changed_lines) {
          html += "changed lines: " + data.lines+"<br/>";
        }
        if(data.message) {
          html += data.message+"<br/>";
        }
        if(data.lines) {
          html += "LOC: " + data.lines+"<br/>";
        }
		html += "</div>"
        tip.innerHTML =  html; 
    }


  infovizContainer = document.getElementById('infovis');
  containerParentNode = infovizContainer.parentNode
  containerParentNode.removeChild(infovizContainer);
  newInfovizContainer = document.createElement('div');
  newInfovizContainer.setAttribute('id', 'infovis');
  containerParentNode.appendChild(newInfovizContainer);
  //end
  //init TreeMap
  var tm = new $jit.TM.Squarified({
    //where to inject the visualization
    injectInto: 'infovis',
    //parent box title heights
    titleHeight: 15,
    //enable animations
    animate: animate,
    //box offsets
    offset: 1,
	constrained:true,
	levelsToShow:2,
    //Attach left and right click events
    Events: {
      enable: true,
      onClick: function(node) {
        if(node) tm.enter(node);
      },
      onRightClick: function() {
        tm.out();
      }
    },
    duration: 1000,
    //Enable tips
    Tips: {
      enable: true,
      //add positioning offsets
      offsetX: 20,
      offsetY: 20,
      //implement the onShow method to
      //add content to the tooltip when a node
      //is hovered
      onShow: tooltip
    },
	onMouseEnter: function(node, eventInfo, e) {  
      viz.canvas.getElement().style.backgroundColor = '#FF00FF';  
    },  
    //Add the name of the node in the correponding label
    //This method is called once, on label creation.
    onCreateLabel: function(domElement, node){
        domElement.innerHTML = node.name;
        var style = domElement.style;
        style.display = '';
        style.border = '1px solid transparent';
        domElement.onmouseover = function() {
          style.border = '1px solid #9FD4FF';
        };
        domElement.onmouseout = function() {
          style.border = '1px solid transparent';
        };
    }
  });
  tm.loadJSON(json);
  tm.refresh();
  //end
  //add events to radio buttons
  var sq = $jit.id('r-sq'),
      st = $jit.id('r-st'),
      sd = $jit.id('r-sd');
  var util = $jit.util;
  util.addEvent(sq, 'change', function() {
    if(!sq.checked) return;
    util.extend(tm, new $jit.Layouts.TM.Squarified);
    tm.refresh();
  });
  util.addEvent(st, 'change', function() {
    if(!st.checked) return;
    util.extend(tm, new $jit.Layouts.TM.Strip);
    tm.layout.orientation = "v";
    tm.refresh();
  });
  util.addEvent(sd, 'change', function() {
    if(!sd.checked) return;
    util.extend(tm, new $jit.Layouts.TM.SliceAndDice);
    tm.layout.orientation = "v";
    tm.refresh();
  });
  //add event to the back button
  var back = $jit.id('back');
  $jit.util.addEvent(back, 'click', function() {
    tm.out();
  });
}

function createAuthorDropdownMenue(){
	authors = ${authors}
	for(id in authors){
	    opt = document.createElement("option");
	    document.getElementById("dropdown_authors").options.add(opt);
	    opt.text = authors[id];
	    opt.value = authors[id];
	}
}

</script>

<script language="javascript" type="text/javascript" src="./Jit/jit-yc.js"></script>
</head>

<body onload="displayTreemap('files_view');createAuthorDropdownMenue();">
<div id="container">

<div id="left-container">



<div class="text">
<h4>
Animated Squarified TreeMaps    
</h4> 

            <b>Left click</b> to set a node as root for the visualization.<br /><br />
            <b>Right click</b> to set the parent node as root for the visualization.<br /><br />
            
</div>

<div id="id-list">
<table>
    <tr>
        <td>
            <label for="r-sq">Squarified </label>
        </td>
        <td>
            <input type="radio" id="r-sq" name="layout" checked="checked" value="left" />
        </td>
    </tr>
    <tr>
         <td>
            <label for="r-st">Strip </label>
         </td>
         <td>
            <input type="radio" id="r-st" name="layout" value="top" />
         </td>
    <tr>
         <td>
            <label for="r-sd">SliceAndDice </label>
          </td>
          <td>
            <input type="radio" id="r-sd" name="layout" value="bottom" />
          </td>
    </tr>
	<tr>
		<td>
		<select id="dropdown_authors" onChange="javascript:displayTreemap('author_view')" style="visibility:hidden;">
		</select>
		</td>
	</tr>
    
	<tr>
		<td>
			<div class="wrapper">
				<div class="mainmenu">
					<ul class="menu">
						<li class="list">
						 <a href="#view" class="category" id="view"><img id='selected_view' src='./img/files_button.png'/></a>
						 <ul class="submenu">
						  <li><a href="javascript:displayTreemap('git_view');" class="git_view"></a></li>
						  <li><a href="javascript:displayTreemap('files_view');" class="files_view"></a></li>
						  <li><a href="javascript:displayTreemap('author_view');" class="author_view"></a></li>
						 </ul>
						</li>
					</ul>
				<!-- end mainmenu --></div>
			<!-- end wrapper --></div>
		</td>
	</tr>
</table>
</div>

 


<a id="back" href="#" class="theme button white">Go to Parent</a>
</div>
 
<div id="center-container">
    <div id="infovis"></div>    
</div>


<div id="right-container">
<img src="./img/heatmap.jpg" height="100%" width="30px" /> 

<div id="inner-details"></div>

</div>

<div id="log"></div>
</div>
</body>
</html>
