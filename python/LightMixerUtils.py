import nuke
from datetime import date

###################################
##### LIGHT LAYER FUNCTIONS ######
###################################

def Remove_Layer_Button():
    """
    Remove the current light layer with all of its knobs and all of its corresponding internal nodes.

    """

    import re
    k = nuke.thisKnob()
    kName = k.name()
    layerNumber = ''.join(filter(str.isdigit, kName))

    for n in nuke.allNodes():
        if "AOV" + layerNumber in n['label'].getValue():
            nuke.delete(n)

    thisGroup = nuke.thisNode()
    allKnobs = list(thisGroup.knobs().keys())

    for knobName in allKnobs:

        if (re.findall("\d+", layerNumber) == re.findall("\d+", knobName)):
            thisGroup.removeKnob(thisGroup[knobName])
        continue


    n = nuke.thisNode()
    knobs = thisGroup.knobs()  

    pointsOrig = []
    for knob in knobs:
        if knob[0:7] == "lightID":
            id = int(knob[7:])
            pointsOrig.append(id)

    pointsOrig.sort()

    thisGroup['lightCount'].setValue('<b>' + str(len(pointsOrig)) + '</b>')
    points = ','.join(str(i) for i in pointsOrig)
    thisGroup['lights'].setValue(len(pointsOrig))


def Reset_Edits_Button():
    """
    Reset all knobs on this layer to their default value

    """

    n = nuke.thisNode()
    k = nuke.thisKnob()
    nLabel = k.name()
    layerNumber = "".join(filter(str.isdigit, nLabel))

    n['IntensityAOV' + layerNumber].setValue(1)
    n['ExposureAOV' + layerNumber].setValue(0)
    n['OverallSatAOV' + layerNumber].setValue(1)
    n['RGBColourAOV' + layerNumber].setValue([1, 1, 1])
    n['HueAOV' + layerNumber].setValue(0)
    n['SaturationAOV' + layerNumber].setValue(0)
    n['ValueAOV' + layerNumber].setValue(1)
    n['TemperatureAOV' + layerNumber].setValue(6600)
    n['DisableTemperatureAOV' + layerNumber].setValue(0)
    n['SubtractAOV' + layerNumber].setValue(0)


def Houdini_Copy_Button():
    """
    Wrap all the edits made on this layer into a dictionary + the current date and name of the nuke script. Finally, store that in the clipboard so it can be used to import in Houdini.

    """
    from PySide2.QtGui import QGuiApplication

    n = nuke.thisNode()
    k = nuke.thisKnob()
    nLabel = k.name()
    layerNumber = "".join(filter(str.isdigit, nLabel))

    #Define HSV/RGB knob label text
    RGB = '<big><font style="background-color:#806060;">R<font style="background-color:#608071;">G<font style="background-color:#606680;">B'
    HSV = '<big><font style="background-color:#807460;">H<font style="background-color:#606680;">S<font style="background-color:#80607d;">V'

    #Adding date and script name to dictionary
    scriptName = nuke.scriptName().split('/')
    dict = {'comment_info': f'Date of import: {date.today()} \nImport from: {scriptName[-1]}', }

    AOVPrefix = n['AOVPattern'].value()
    AOVName = n['LightAOV' + layerNumber].value()
    if AOVPrefix.lower() in AOVName.lower():
        AOVNameSliced = AOVName[len(AOVPrefix):]
    else:
        AOVNameSliced = AOVName

    IntensityValue = n['IntensityAOV' + layerNumber].value()
    ExposureValue = n['ExposureAOV' + layerNumber].value()


    if n['HSV_RGBAOV' + layerNumber].label() == HSV:

        for node in n.nodes():
            if "Colour AdjustmentsAOV" + layerNumber in node['label'].getValue():
                RGBValues = node['multiply'].value()

    if n['HSV_RGBAOV' + layerNumber].label() == RGB:
        RGBValues = n['RGBColourAOV' + layerNumber].value()

    # Get RGB Temperature value and multiply it with rgb values to be included when copying to houdini
    if n['DisableTemperatureAOV' + layerNumber].value() == 0:
        for node in n.nodes():
            if "TemperatureAOV" + layerNumber in node['label'].getValue():
                TemperatureValue = node['multiply'].value()
                TemperatureValue = TemperatureValue[:-1]

                RGBValues = [x * y for x, y in zip(RGBValues, TemperatureValue)]

    RedValue = RGBValues[0]
    GreenValue = RGBValues[1]
    BlueValue = RGBValues[2]
    dict[AOVNameSliced] = [
        IntensityValue,
        ExposureValue,
        RedValue,
        GreenValue,
        BlueValue,
    ]


    clipboardText = f"""{dict}"""

    # Qt way to store something in the clipboard
    QGuiApplication.clipboard().setText(clipboardText)
    nuke.message(f'<font color=green><h3><center>{AOVNameSliced} '"""
Copy Successful, proceed pasting in Houdini
<font color=orange>Important! 
Overall Saturation information not copied across.""")


def HSV_RGB_Button():
    """
    Allow for switching back and forth between RGB and HSV colour modes and convert their values to the other if the button is pressed.

    """

    def HSV_to_RGB():

        def HSV_to_RGB_Algorithm(h, s, v,):
            h = h % 360  
            s = max(0, min(1, s))  
            v = max(0, min(1, v)) 

            c = v * s
            x = c * (1 - abs((h / 60) % 2 - 1))
            m = v - c

            if 0 <= h < 60:
                r, g, b = c, x, 0
            elif 60 <= h < 120:
                r, g, b = x, c, 0
            elif 120 <= h < 180:
                r, g, b = 0, c, x
            elif 180 <= h < 240:
                r, g, b = 0, x, c
            elif 240 <= h < 300:
                r, g, b = x, 0, c
            else:
                r, g, b = c, 0, x

            r, g, b = (r + m, g + m, b + m)

            return r, g, b


        hueValue = float(nuke.thisNode()['HueAOV' + layerNumber].value())
        saturationValue = float((nuke.thisNode()['SaturationAOV' + layerNumber].value()))
        valueValue = float(nuke.thisNode()['ValueAOV' + layerNumber].value())

        rgbValues = HSV_to_RGB_Algorithm(hueValue, saturationValue, valueValue)

        nuke.thisNode()['RGBColourAOV' + layerNumber].setValue([rgbValues[0], rgbValues[1], rgbValues[2]])

        nuke.thisNode()['HueAOV' + layerNumber].setVisible(False)
        nuke.thisNode()['SaturationAOV' + layerNumber].setVisible(False)
        nuke.thisNode()['ValueAOV' + layerNumber].setVisible(False)

        nuke.thisNode()['RGBColourAOV' + layerNumber].setVisible(True)


        nuke.thisNode().begin()
        gradeNodes = nuke.allNodes('Grade')

        for node in gradeNodes:
            if "Colour AdjustmentsAOV" + layerNumber in node['label'].value():
                node['modecheck'].setValue(1)

        nuke.thisNode().end()

    def RGB_to_HSV():

        def RGB_to_HSV_Algorithm(r, g, b):
            maxVal = max(r, g, b)
            minVal = min(r, g, b)

            delta = maxVal - minVal

            if delta == 0:
                h = 0
            elif maxVal == r:
                h = 60 * ((g - b) / delta % 6)
            elif maxVal == g:
                h = 60 * ((b - r) / delta + 2)
            elif maxVal == b:
                h = 60 * ((r - g) / delta + 4)

            s = 0 if maxVal == 0 else delta / maxVal
            v = maxVal

            return h, s, v

        rgbValues = nuke.thisNode()['RGBColourAOV' + layerNumber].value()

        redValue = rgbValues[0]
        greenValue = rgbValues[1]
        blueValue = rgbValues[2]

        rgbValues = RGB_to_HSV_Algorithm(redValue, greenValue, blueValue)

        nuke.thisNode()['HueAOV' + layerNumber].setValue(rgbValues[0])
        nuke.thisNode()['SaturationAOV' + layerNumber].setValue((rgbValues[1]))
        nuke.thisNode()['ValueAOV' + layerNumber].setValue(rgbValues[2])

        nuke.thisNode()['HueAOV' + layerNumber].setVisible(True)
        nuke.thisNode()['SaturationAOV' + layerNumber].setVisible(True)
        nuke.thisNode()['ValueAOV' + layerNumber].setVisible(True)

        nuke.thisNode()['RGBColourAOV' + layerNumber].setVisible(False)

        nuke.thisNode().begin()
        gradeNodes = nuke.allNodes('Grade')

        for node in gradeNodes:
            if "Colour AdjustmentsAOV" + layerNumber in node['label'].value():
                node['modecheck'].setValue(0)

        nuke.thisNode().end()


    #Define HSV/RGB knob label text
    RGB = '<big><font style="background-color:#806060;">R<font style="background-color:#608071;">G<font style="background-color:#606680;">B'
    HSV = '<big><font style="background-color:#807460;">H<font style="background-color:#606680;">S<font style="background-color:#80607d;">V'

    knob = nuke.thisKnob()
    node = nuke.thisNode()
    options = [RGB, HSV]
    knob.setLabel(options[int(knob.label() == options[0])])

    knobName = nuke.thisKnob().name()
    layerNumber = ''.join(filter(str.isdigit, knobName))

    if knob.label() == RGB:
        HSV_to_RGB()

    if knob.label() == HSV:
        RGB_to_HSV()


############# KNOBCHANGED FUNCTIONS #############
def Dyanmic_Mask_Input():
    """
    Callback function for creating/deleting internal mask setup whenever the mask input is enabled/disabled.
    Also includes workaround for the nuke quirk of empty input handles when input node is deleted.

    """
    n = nuke.thisNode()
    k = nuke.thisKnob()
    nLabel = n["label"].value()
    layerNumber = "".join(filter(str.isdigit, nLabel))


    for n in nuke.allNodes():
        if "FromAOV" + layerNumber in n['label'].getValue():
            fromMerge = nuke.toNode(n.name())

        if "PlusAOV" + layerNumber in n['label'].getValue():
            plusMerge = nuke.toNode(n.name())

        if "CopyAOV" + layerNumber in n['label'].getValue():
            copyNode = nuke.toNode(n.name())

        if "mainShuffleAOV" + layerNumber in n['label'].getValue():
            shuffleNode = nuke.toNode(n.name())

    parentName = n.parent().name()
    thisGroup = nuke.toNode(parentName)

    if k.name() == "addMaskInputAOV" + layerNumber and k.value() == 1:

        thisGroup['maskChannelMaskAOV' + layerNumber].setEnabled(True)
        thisGroup['InvertMaskAOV' + layerNumber].setEnabled(True)

        thisGroup['maskChannelMaskAOV' + layerNumber].setValue('rgba.alpha')
        # setting value on invert mask knob back and forth because it only sets the setEnabled flag when interacted with it
        thisGroup['InvertMaskAOV' + layerNumber].setValue(1)
        thisGroup['InvertMaskAOV' + layerNumber].setValue(0)

        ShuffleAOV = nuke.toNode(shuffleNode.name())
        nameAOV = ShuffleAOV['in'].value()

        maskInput = nuke.nodes.Input()
        maskInput['name'].setValue('Mask' + layerNumber + '_' + nameAOV)
        maskInput['label'].setValue('MaskAOV' + layerNumber)
        maskInput['xpos'].setValue(int(fromMerge['xpos'].value()) - 250)
        maskInput['ypos'].setValue(int(fromMerge['ypos'].value()))

        fromMerge.setInput(2, maskInput)
        plusMerge.setInput(2, maskInput)
        copyNode.setInput(2, maskInput)

    if k.name() == "addMaskInputAOV" + layerNumber and k.value() == 0:

        thisGroup['maskChannelMaskAOV' + layerNumber].setEnabled(False)
        thisGroup['InvertMaskAOV' + layerNumber].setEnabled(False)

        thisGroup['maskChannelMaskAOV' + layerNumber].setValue('none')

        # setting value on invert mask knob back and forth because it only sets the setEnabled flag when interacted with it
        thisGroup['InvertMaskAOV' + layerNumber].setValue(1)
        thisGroup['InvertMaskAOV' + layerNumber].setValue(0)

        for inputNodes in nuke.allNodes('Input'):
            if "MaskAOV" + layerNumber in inputNodes['label'].getValue():
                thisInputindex = inputNodes['number'].value()
                thisGroup.setInput(int(thisInputindex), None)
                nuke.delete(inputNodes)

        allInputNodes = nuke.allNodes('Input')
        allMaskInputNodes = allInputNodes[:-1]

        i = len(allMaskInputNodes)

        for inputNodes in allMaskInputNodes:

            index = inputNodes['number'].value()

            connectedNode = thisGroup.input(int(index))
            if connectedNode != None:
                connectedNode = connectedNode['name'].getValue()

            thisGroup.setInput(int(index), None)

            inputNodes['number'].setValue(float(i))
            with nuke.root():
                connectedNode = nuke.toNode(connectedNode)
            thisGroup.setInput(i, connectedNode)
            print("Index:", index)
            print("new index:", i)

            i = i - 1


def Dynamic_Group_Label():
    """
    Callback function for dynamically adjusting layer name & mask input name based on what AOV is selected. 

    """
    n = nuke.thisNode()
    k = nuke.thisKnob()
    nLabel = n["label"].value()
    layerNumber = "".join(filter(str.isdigit, nLabel))
    parentName = n.parent().name()
    g = nuke.toNode(parentName)
    if k.name() == "in":
        aov = n["in"].value()
        g["lightID" + layerNumber].setLabel(str(aov))

        for n in nuke.allNodes():
            if "MaskAOV" + layerNumber in n['label'].getValue():
                g = nuke.toNode(n.name())
                g['name'].setValue('Mask_' + str(aov))


def Dynamic_Temperature_Knob():
    """
    Callback function for enabling/disabling temperature slider.

    """
    n = nuke.thisNode()
    k = nuke.thisKnob()
    nLabel = n["label"].value()
    layerNumber = "".join(filter(str.isdigit, nLabel))
    parentName = n.parent().name()
    g = nuke.toNode(parentName)
    if k.name() == "disable" and k.value() == 1:
     g["TemperatureAOV" + layerNumber].setEnabled(False)
    if k.name() == "disable" and k.value() == 0:
     g["TemperatureAOV" + layerNumber].setEnabled(True)


###################################
##### LAYER CONTROL FUNCTIONS ######
###################################

def Add_Light_Layer_Button():
    """
    Function for creating a single additional light layer. 
    In order to keep info text at the bottom of gizmo it needs to be deleted and recreated.

    """
    ### Housekeeping before creating light layer ###
    thisGroup = nuke.thisNode()
    allKnobs = thisGroup.knobs()
    lightIDKnobs = [knob for knob in allKnobs if knob.startswith("lightID")]
    uniqueNumbers = [int(knob.replace("lightID", "")) for knob in lightIDKnobs]
    knobCounter = str(max(uniqueNumbers) + 1)

    originalInfoText = thisGroup['info'].value()
    thisGroup.removeKnob(thisGroup['info'])

    Light_Layer_Creation(thisGroup=thisGroup, knobCounter=knobCounter)

    knobInfoText = nuke.Text_Knob('info', '')
    thisGroup.addKnob(knobInfoText)
    knobInfoText.setValue(originalInfoText)
    knobInfoText.setFlag(nuke.STARTLINE)


def Light_Layer_Creation(thisGroup, knobCounter):
    """
    Main function for creating light layer knobs and internal nodes.

    """

    #Create all internal nodes
    thisGroup.begin()
    output = nuke.toNode('Output1')
    upstreamNode = output.input(0)
    startNodeName = upstreamNode.name()
    startNode = nuke.toNode(str(startNodeName))

    newX = startNode['xpos'].value()
    newY = startNode['ypos'].value()

    newDot = nuke.nodes.Dot()
    newDot.setSelected(True)
    newDot.setInput(0, startNode)
    newDot['label'].setValue('AOV' + knobCounter)
    newDot['note_font_size'].setValue(0)
    newDot['xpos'].setValue(int(newX) + 34)
    newDot['ypos'].setValue(int(newY) + 400)

    newDot2 = nuke.nodes.Dot()
    newDot2.setSelected(True)
    newDot2.setInput(0, newDot)
    newDot2['label'].setValue('AOV' + knobCounter)
    newDot2['note_font_size'].setValue(0)
    newDot2['xpos'].setValue(int(newDot['xpos'].value()) + 300)
    newDot2['ypos'].setValue(int(newDot['ypos'].value()))

    # creating noOp for internal knobchanged callbacks
    NoOpNode = nuke.nodes.NoOp()
    NoOpNode.setInput(0, newDot2)
    NoOpNode['label'].setValue('AOV' + knobCounter)
    NoOpNode['xpos'].setValue(int(newDot2['xpos'].value()) + 200)
    NoOpNode['ypos'].setValue(int(newDot2['ypos'].value()) - 12)

    knobCheckBox = nuke.Boolean_Knob('addMaskInputAOV' + knobCounter, 'internal add mask for layer ' + knobCounter)
    NoOpNode.addKnob(knobCheckBox)
    knobCheckBox.setFlag(nuke.STARTLINE)

    mainShuffle = nuke.nodes.Shuffle()
    mainShuffle.setSelected(True)
    mainShuffle.setInput(0, newDot2)
    mainShuffle['label'].setValue('mainShuffleAOV' + knobCounter)
    mainShuffle['xpos'].setValue(int(newDot2['xpos'].value()) - 34)
    mainShuffle['ypos'].setValue(int(newDot2['ypos'].value()) + 200)
    mainShuffle['in'].setValue('none')

    fromMergeNode = nuke.nodes.Merge2()
    fromMergeNode.setSelected(True)
    fromMergeNode.setInput(0, newDot)
    fromMergeNode.setInput(1, mainShuffle)
    fromMergeNode['label'].setValue('FromAOV' + knobCounter)
    fromMergeNode['operation'].setValue('from')
    fromMergeNode['output'].setValue('rgb')
    fromMergeNode['xpos'].setValue(int(newDot['xpos'].value()) - 34)
    fromMergeNode['ypos'].setValue(int(newDot['ypos'].value()) + 200)

    subtractMultiply = nuke.nodes.Multiply()
    subtractMultiply.setSelected(True)
    subtractMultiply.setInput(0, mainShuffle)
    subtractMultiply['channels'].setValue('rgb')
    subtractMultiply['label'].setValue('SubtractAOV' + knobCounter)
    subtractMultiply['xpos'].setValue(int(mainShuffle['xpos'].value()))
    subtractMultiply['ypos'].setValue(int(mainShuffle['ypos'].value()) + 200)

    expGrade = nuke.nodes.Grade()
    expGrade.setSelected(True)
    expGrade.setInput(0, subtractMultiply)
    expGrade['label'].setValue('Exposure & IntensityAOV' + knobCounter)
    expGrade['xpos'].setValue(int(subtractMultiply['xpos'].value()))
    expGrade['ypos'].setValue(int(subtractMultiply['ypos'].value()) + 200)

    overallSatNode = nuke.nodes.Saturation()
    overallSatNode.setSelected(True)
    overallSatNode.setInput(0, expGrade)
    overallSatNode['label'].setValue('Overall SaturationAOV' + knobCounter)
    overallSatNode['xpos'].setValue(int(expGrade['xpos'].value()))
    overallSatNode['ypos'].setValue(int(expGrade['ypos'].value()) + 200)

    colourGrade = nuke.nodes.Grade()
    colourGrade.setSelected(True)
    colourGrade.setInput(0, overallSatNode)
    colourGrade['label'].setValue('Colour AdjustmentsAOV' + knobCounter)
    colourGrade['xpos'].setValue(int(overallSatNode['xpos'].value()))
    colourGrade['ypos'].setValue(int(overallSatNode['ypos'].value()) + 200)

    # Create user knobs for RGB HSV conversion
    colourGrade.addKnob(nuke.Boolean_Knob('modecheck', 'mode check'))
    colourGrade['modecheck'].setValue(1)

    colourGrade.addKnob(nuke.Double_Knob('red', 'red'))
    colourGrade.addKnob(nuke.Double_Knob('green', 'green'))
    colourGrade.addKnob(nuke.Double_Knob('blue', 'blue'))

    colourGrade.addKnob(nuke.Double_Knob('hueint', 'hueint'))
    colourGrade.addKnob(nuke.Double_Knob('satint', 'satint'))
    colourGrade.addKnob(nuke.Double_Knob('valueint', 'valueint'))

    colourGrade.addKnob(nuke.Double_Knob('c', 'c'))
    colourGrade.addKnob(nuke.Double_Knob('x', 'x'))
    colourGrade.addKnob(nuke.Double_Knob('m', 'm'))

    colourGrade.addKnob(nuke.Double_Knob('redHSV', 'redHSV'))
    colourGrade.addKnob(nuke.Double_Knob('greenHSV', 'greenHSV'))
    colourGrade.addKnob(nuke.Double_Knob('blueHSV', 'blueHSV'))

    colourGrade['c'].setExpression('satint * valueint')
    colourGrade['x'].setExpression('c * (1 - abs((hueint / 60) % 2 - 1))')
    colourGrade['m'].setExpression('valueint - c')

    colourGrade['redHSV'].setExpression(
        '(hueint >= 0 && hueint < 60 ? this.c : hueint >= 60 && hueint < 120 ? this.x : hueint >= 120 && hueint < 180 ? 0 : hueint >= 180 && hueint < 240 ? 0 : hueint >= 240 && hueint < 300 ? this.x : this.c) + this.m')
    colourGrade['greenHSV'].setExpression(
        '(hueint >= 0 && hueint < 60 ? this.x : hueint >= 60 && hueint < 120 ? this.c : hueint >= 120 && hueint < 180 ? this.c : hueint >= 180 && hueint < 240 ? this.x : hueint >= 240 && hueint < 300 ? 0 : 0) + this.m')
    colourGrade['blueHSV'].setExpression(
        '(hueint >= 0 && hueint < 60 ? 0 : hueint >= 60 && hueint < 120 ? 0 : hueint >= 120 && hueint < 180 ? this.x : hueint >= 180 && hueint < 240 ? this.c : hueint >= 240 && hueint < 300 ? this.c : this.x) + this.m')

    newDot3 = nuke.nodes.Dot()
    newDot3.setSelected(True)
    newDot3.setInput(0, colourGrade)
    newDot3['label'].setValue('AOV' + knobCounter)
    newDot3['note_font_size'].setValue(0)
    newDot3['xpos'].setValue(int(colourGrade['xpos'].value()) + 34)
    newDot3['ypos'].setValue(int(colourGrade['ypos'].value()) + 100)

    newDot4 = nuke.nodes.Dot()
    newDot4.setSelected(True)
    newDot4.setInput(0, newDot3)
    newDot4['label'].setValue('AOV' + knobCounter)
    newDot4['note_font_size'].setValue(0)
    newDot4['xpos'].setValue(int(newDot3['xpos'].value()) - 150)
    newDot4['ypos'].setValue(int(newDot3['ypos'].value()))

    tGrade = nuke.nodes.Grade()
    tGrade.setSelected(True)
    tGrade.setInput(0, newDot3)
    tGrade['label'].setValue('TemperatureAOV' + knobCounter)
    tGrade['xpos'].setValue(int(newDot3['xpos'].value()) - 34)
    tGrade['ypos'].setValue(int(newDot3['ypos'].value()) + 100)

    tfromMergeNode = nuke.nodes.Merge2()
    tfromMergeNode.setSelected(True)
    tfromMergeNode.setInput(0, newDot4)
    tfromMergeNode.setInput(1, tGrade)
    tfromMergeNode['label'].setValue('AOV' + knobCounter)
    tfromMergeNode['operation'].setValue('from')
    tfromMergeNode['output'].setValue('rgb')
    tfromMergeNode['xpos'].setValue(int(newDot4['xpos'].value()) - 34)
    tfromMergeNode['ypos'].setValue(int(newDot4['ypos'].value()) + 100)

    tSaturation = nuke.nodes.Saturation()
    tSaturation.setSelected(True)
    tSaturation.setInput(0, tfromMergeNode)
    tSaturation['label'].setValue('AOV' + knobCounter)
    tSaturation['xpos'].setValue(int(tfromMergeNode['xpos'].value()))
    tSaturation['ypos'].setValue(int(tfromMergeNode['ypos'].value()) + 100)
    tSaturation['saturation'].setValue(0)

    tplusMergeNode = nuke.nodes.Merge2()
    tplusMergeNode.setSelected(True)
    tplusMergeNode.setInput(0, tGrade)
    tplusMergeNode.setInput(1, tSaturation)
    tplusMergeNode['label'].setValue('AOV' + knobCounter)
    tplusMergeNode['operation'].setValue('plus')
    tplusMergeNode['output'].setValue('rgb')
    tplusMergeNode['xpos'].setValue(int(tGrade['xpos'].value()))
    tplusMergeNode['ypos'].setValue(int(tGrade['ypos'].value()) + 100)

    newDot5 = nuke.nodes.Dot()
    newDot5.setSelected(True)
    newDot5.setInput(0, tplusMergeNode)
    newDot5['label'].setValue('AOV' + knobCounter)
    newDot5['note_font_size'].setValue(0)
    newDot5['xpos'].setValue(int(tplusMergeNode['xpos'].value()) + 34)
    newDot5['ypos'].setValue(int(tplusMergeNode['ypos'].value()) + 200)

    plusMergeNode = nuke.nodes.Merge2()
    plusMergeNode.setSelected(True)
    plusMergeNode.setInput(0, fromMergeNode)
    plusMergeNode.setInput(1, newDot5)
    plusMergeNode['label'].setValue('PlusAOV' + knobCounter)
    plusMergeNode['operation'].setValue('plus')
    plusMergeNode['output'].setValue('rgb')
    plusMergeNode['xpos'].setValue(int(startNode['xpos'].value()))
    plusMergeNode['ypos'].setValue(int(newDot5['ypos'].value()) - 12)

    newDot6 = nuke.nodes.Dot()
    newDot6.setSelected(True)
    newDot6.setInput(0, mainShuffle)
    newDot6['label'].setValue('AOV' + knobCounter)
    newDot6['note_font_size'].setValue(0)
    newDot6['xpos'].setValue(int(mainShuffle['xpos'].value()) + 250)
    newDot6['ypos'].setValue(int(mainShuffle['ypos'].value()) + 12)

    newDot7 = nuke.nodes.Dot()
    newDot7.setSelected(True)
    newDot7.setInput(0, newDot6)
    newDot7['label'].setValue('AOV' + knobCounter)
    newDot7['note_font_size'].setValue(0)
    newDot7['xpos'].setValue(int(newDot6['xpos'].value()))
    newDot7['ypos'].setValue(int(newDot5['ypos'].value()) + 212)

    switch1 = nuke.nodes.Switch()
    switch1.setSelected(True)
    switch1.setInput(0, newDot5)
    switch1.setInput(1, newDot7)
    switch1['label'].setValue('AOV' + knobCounter)
    switch1['xpos'].setValue(int(newDot5['xpos'].value()) - 34)
    switch1['ypos'].setValue(int(newDot5['ypos'].value()) + 200)

    newDot8 = nuke.nodes.Dot()
    newDot8.setSelected(True)
    newDot8.setInput(0, switch1)
    newDot8['label'].setValue('AOV' + knobCounter)
    newDot8['note_font_size'].setValue(0)
    newDot8['xpos'].setValue(int(switch1['xpos'].value()) + 34)
    newDot8['ypos'].setValue(int(switch1['ypos'].value()) + 100)

    newDot9 = nuke.nodes.Dot()
    newDot9.setSelected(True)
    newDot9.setInput(0, newDot8)
    newDot9['label'].setValue('AOV' + knobCounter)
    newDot9['note_font_size'].setValue(0)
    newDot9['xpos'].setValue(int(newDot8['xpos'].value()))
    newDot9['ypos'].setValue(int(newDot8['ypos'].value()) + 300)

    secondShuffle = nuke.nodes.Shuffle()
    secondShuffle.setSelected(True)
    secondShuffle.setInput(0, newDot8)
    secondShuffle['label'].setValue('AOV' + knobCounter)
    secondShuffle['xpos'].setValue(int(newDot8['xpos'].value()) - 175)
    secondShuffle['ypos'].setValue(int(newDot8['ypos'].value()) - 12)
    secondShuffle['out'].setExpression('parent.' + mainShuffle['name'].value() + '.in')

    remove = nuke.nodes.Remove()
    remove.setSelected(True)
    remove.setInput(0, secondShuffle)
    remove['label'].setValue('AOV' + knobCounter)
    remove['xpos'].setValue(int(secondShuffle['xpos'].value()))
    remove['ypos'].setValue(int(secondShuffle['ypos'].value()) + 200)
    remove['operation'].setValue('remove')
    remove['channels'].setValue('rgba')

    copy = nuke.nodes.Copy()
    copy.setSelected(True)
    copy.setInput(0, plusMergeNode)
    copy.setInput(1, remove)
    copy['label'].setValue('CopyAOV' + knobCounter)
    copy['xpos'].setValue(int(plusMergeNode['xpos'].value()))
    copy['ypos'].setValue(int(remove['ypos'].value()) - 12)
    copy['from0'].setValue('none')
    copy['to0'].setValue('none')
    copy['channels'].setValue('all')

    soloSwitch = nuke.nodes.Switch()
    soloSwitch.setSelected(True)
    soloSwitch.setInput(0, copy)
    soloSwitch.setInput(1, newDot9)
    soloSwitch['label'].setValue('AOV' + knobCounter)
    soloSwitch['xpos'].setValue(int(copy['xpos'].value()))
    soloSwitch['ypos'].setValue(int(newDot9['ypos'].value()) - 12)

    output.setInput(0, soloSwitch)
    output['xpos'].setValue(int(soloSwitch['xpos'].value()))
    output['ypos'].setValue(int(soloSwitch['ypos'].value()) + 300)

    thisGroup.end()

    # Create all needed knobs
    beginGroup = nuke.Tab_Knob("lightID" + knobCounter, 'none', nuke.TABBEGINGROUP)
    thisGroup.addKnob(beginGroup)

    thisGroup.begin()
    shuffleNodeNodes = nuke.allNodes('Shuffle')
    for node in shuffleNodeNodes:
        if "AOV" + knobCounter in node['label'].value():
            shuffleLinkName = node['name'].value()

    thisGroup.end()

    knobLink = nuke.Link_Knob('LightAOV' + knobCounter, 'Light AOV')
    knobLink.setLink(thisGroup.name() + '.' + shuffleLinkName + '.in')
    thisGroup.addKnob(knobLink)
    knobLink.setTooltip('Select light AOV to adjust')

    knobRemoveLayerPython = nuke.PyScript_Knob('removeLayerAOV' + knobCounter, 'Remove Layer', """from LightMixerUtils import * 
Remove_Layer_Button()""")
    thisGroup.addKnob(knobRemoveLayerPython)
    knobRemoveLayerPython.setTooltip(
        'Remove this layer and its adjustments from this thisGroup. This does not remove the adjusted AOV from the render')

    knobCheckBox = nuke.Boolean_Knob('SoloAOV' + knobCounter, 'View AOV')
    thisGroup.addKnob(knobCheckBox)
    knobCheckBox.setTooltip('View just the selected AOV and the changes made to it')
    knobCheckBox.setFlag(nuke.STARTLINE)

    knobCheckBox = nuke.Boolean_Knob('EnableAOV' + knobCounter, 'Enable edits')
    thisGroup.addKnob(knobCheckBox)
    knobCheckBox.setFlag(nuke.STARTLINE)
    knobCheckBox.setValue(1)
    knobCheckBox.setTooltip('Enable or disable the adjustments made to the selected AOV on this layer')

    knobCheckBox = nuke.Boolean_Knob('SubtractAOV' + knobCounter, 'Subtract Light')
    thisGroup.addKnob(knobCheckBox)
    knobCheckBox.setTooltip('Subtract selected AOV from rgba/beauty. Edits made to the light will not be visible')

    knobCheckBox = nuke.Boolean_Knob('CopyAOV' + knobCounter, 'Shuffle back AOV')
    knobCheckBox.setValue(1)
    thisGroup.addKnob(knobCheckBox)
    knobCheckBox.setTooltip(
        'Shuffle back adjusted AOV. If disabled the changes made to the light are only visible in the beauty/rgba')

    knobPython = nuke.PyScript_Knob('ResetAOV' + knobCounter, 'Reset Edits', """from LightMixerUtils import * 
Reset_Edits_Button()""")
    thisGroup.addKnob(knobPython)
    knobPython.setTooltip('Reset the adjustments made to the selected AOV')

    knobPython = nuke.PyScript_Knob('CopyAdjAOV' + knobCounter, 'Houdini Copy', """from LightMixerUtils import * 
Houdini_Copy_Button()""")
    thisGroup.addKnob(knobPython)
    knobPython.setTooltip("""This button copies an editLight node with the adjustments made on this layer. You can then paste it into houdini by hitting tab and searching for "Nuke LightMixer Import". 
If it can find the correct light it will automatically add the right prim path to the node as well. However, it will still work if it can't find it.""")

    knobIntensity = nuke.Double_Knob('IntensityAOV' + knobCounter, 'Intensity')
    thisGroup.addKnob(knobIntensity)
    knobIntensity.setRange(0, 10)
    knobIntensity.setValue(1)
    knobIntensity.setTooltip('Adjust Intensity of light (essentially just a multiply)')

    knobExposure = nuke.Double_Knob('ExposureAOV' + knobCounter, 'Exposure')
    thisGroup.addKnob(knobExposure)
    knobExposure.setRange(-5, 5)
    knobExposure.setTooltip('Adjust Exposure of selected light in stops')

    knobOverallSat = nuke.Double_Knob('OverallSatAOV' + knobCounter, 'Overall Saturation')
    thisGroup.addKnob(knobOverallSat)
    knobOverallSat.setRange(0, 4)
    knobOverallSat.setTooltip('Adjust Saturation of selected AOV')
    knobOverallSat.setValue(1)

    knobText = nuke.Text_Knob('ModeAOV' + knobCounter, 'Colour Mode:', )
    thisGroup.addKnob(knobText)
    knobText.setValue(' ')
    knobText.setFlag(nuke.STARTLINE)

    knobPython = nuke.PyScript_Knob('HSV_RGBAOV' + knobCounter, '<big><font style="background-color:#806060;">R<font style="background-color:#608071;">G<font style="background-color:#606680;">B', """from LightMixerUtils import * 
HSV_RGB_Button()""")
    thisGroup.addKnob(knobPython)
    knobPython.setTooltip(
        'Changes between RGB and HSV to adjust the light colour. The enetered values in either mode will be converted to the other when pressing this button')

    knobRGB = nuke.Color_Knob('RGBColourAOV' + knobCounter, 'RGB')
    thisGroup.addKnob(knobRGB)
    knobRGB.setValue([1, 1, 1])
    knobRGB.setTooltip('Multiply the red, green and blue channels independently')

    knobHue = nuke.Double_Knob('HueAOV' + knobCounter, 'Hue')
    thisGroup.addKnob(knobHue)
    knobHue.setRange(0, 360)
    knobHue.setTooltip('Adjust the Hue of the colour you are adding to the light in HSV')
    knobHue.setVisible(False)

    knobSaturation = nuke.Double_Knob('SaturationAOV' + knobCounter, 'Saturation')
    thisGroup.addKnob(knobSaturation)
    knobSaturation.setRange(0, 1)
    knobSaturation.setTooltip('Adjust the Saturation of the colour you are adding to the light in HSV')
    knobSaturation.setVisible(False)

    knobValue = nuke.Double_Knob('ValueAOV' + knobCounter, 'Value')
    thisGroup.addKnob(knobValue)
    knobValue.setValue(1)
    knobValue.setTooltip('Adjust the Brightness of the colour you are adding to the light in HSV')
    knobValue.setVisible(False)

    knobLink = nuke.Link_Knob('DisableTemperatureAOV' + knobCounter, 'Disable Colour Temperature')
    knobLink.setLink(thisGroup.name() + '.' + tGrade.name() + '.disable')
    thisGroup.addKnob(knobLink)
    thisGroup.begin()
    nuke.toNode(tGrade.name())['disable'].setValue(0)
    thisGroup.end()

    knobTemperature = nuke.Double_Knob('TemperatureAOV' + knobCounter, 'Temperature (k)')
    thisGroup.addKnob(knobTemperature)
    knobTemperature.setTooltip('Adjust colour temperature of the selected AOV in Kelvin. Usable range is between 1000 - 20000. Default white is set at 6600.')
    knobTemperature.setRange(1000, 10000)
    knobTemperature.setValue(6600)

    knobDivider = nuke.Text_Knob('maskLineAOV' + knobCounter, 'Mask')
    thisGroup.addKnob(knobDivider)
    knobDivider.setFlag(nuke.STARTLINE)

    knobLink = nuke.Link_Knob('EnableMaskAOV' + knobCounter, 'Enable Mask')
    knobLink.setLink(thisGroup.name() + '.' + NoOpNode.name() + '.addMaskInputAOV' + knobCounter)
    thisGroup.addKnob(knobLink)

    knobLink = nuke.Link_Knob('maskChannelMaskAOV' + knobCounter, '')
    knobLink.setLink(thisGroup.name() + '.' + fromMergeNode.name() + '.maskChannelMask')
    knobLink.clearFlag(nuke.STARTLINE)
    thisGroup.addKnob(knobLink)
    fromMergeNode['maskChannelMask'].setValue('none')

    knobLink = nuke.Link_Knob('InvertMaskAOV' + knobCounter, 'invert')
    knobLink.setLink(thisGroup.name() + '.' + fromMergeNode.name() + '.invert_mask')
    knobLink.clearFlag(nuke.STARTLINE)
    thisGroup.addKnob(knobLink)
    knobLink.setEnabled(False)

    endGroup = nuke.Tab_Knob('end' + knobCounter, None, nuke.TABENDGROUP)
    thisGroup.addKnob(endGroup)

    knobDivider = nuke.Text_Knob('lastAOV' + knobCounter, '')
    thisGroup.addKnob(knobDivider)
    knobDivider.setFlag(nuke.STARTLINE)


    # Create all expression links
    thisGroup.begin()

    # Setting knobChanged callbacks
    tGrade.knob('knobChanged').setValue("""from LightMixerUtils import * 
Dynamic_Temperature_Knob()""")
    shuffleLinkNode = nuke.toNode(shuffleLinkName)
    shuffleLinkNode.knob('knobChanged').setValue("""from LightMixerUtils import * 
Dynamic_Group_Label()""")
    NoOpNode.knob('knobChanged').setValue("""from LightMixerUtils import * 
Dyanmic_Mask_Input()""")

    # Setting simple node expression links

    subtractMultiply['value'].setExpression('1 - parent.SubtractAOV' + knobCounter)
    fromMergeNode['disable'].setExpression('1 - parent.EnableAOV' + knobCounter)
    plusMergeNode['disable'].setExpression('1 - parent.EnableAOV' + knobCounter)
    copy['disable'].setExpression('1 - parent.CopyAOV' + knobCounter)
    soloSwitch['which'].setExpression('parent.SoloAOV' + knobCounter)
    switch1['which'].setExpression('1 - parent.EnableAOV' + knobCounter)

    plusMergeNode['invert_mask'].setExpression('parent.' + fromMergeNode.name() + '.invert_mask')
    plusMergeNode['maskChannelInput'].setExpression('parent.' + fromMergeNode.name() + '.maskChannelInput')
    copy['invert_mask'].setExpression('parent.' + fromMergeNode.name() + '.invert_mask')
    copy['maskChannelInput'].setExpression('parent.' + fromMergeNode.name() + '.maskChannelInput')

    expGrade['white'].setExpression('parent.IntensityAOV' + knobCounter)
    expGrade['multiply'].setExpression('1 / (2 ** ( parent.ExposureAOV' + knobCounter + '* -1 ) )')
    overallSatNode['saturation'].setExpression('parent.OverallSatAOV' + knobCounter)

    colourGrade['red'].setExpression('modecheck == 1 ? parent.RGBColourAOV' + knobCounter + '.r  : redHSV')
    colourGrade['green'].setExpression('modecheck == 1 ? parent.RGBColourAOV' + knobCounter + '.g  : greenHSV')
    colourGrade['blue'].setExpression('modecheck == 1 ? parent.RGBColourAOV' + knobCounter + '.b  : blueHSV')

    colourGrade['hueint'].setExpression('clamp(parent.HueAOV' + knobCounter + ', 0, 360)')
    colourGrade['satint'].setExpression('clamp(parent.SaturationAOV' + knobCounter + ', 0, 1)')
    colourGrade['valueint'].setExpression('clamp(parent.ValueAOV' + knobCounter + ', 0, 1)')

    colourGrade['multiply'].setValue([0, 5, 2, 1])
    colourGrade['multiply'].setExpression('red', channel=0)
    colourGrade['multiply'].setExpression('green', channel=1)
    colourGrade['multiply'].setExpression('blue', channel=2)

    tGrade['multiply'].setValue([0, 5, 2, 1])
    tGrade['multiply'].setExpression(
        'clamp( parent.TemperatureAOV' + knobCounter + ', 1000, 40000 ) / 100 <= 66 ? 1 : clamp( ( ( ( ( clamp( parent.TemperatureAOV' + knobCounter + ', 1000, 40000 ) / 100 ) - 60 ) ** -0.1332047592 )  * 329.698727446 ), 0, 255 ) / 255',
        channel=0)
    tGrade['multiply'].setExpression(
        'clamp( parent.TemperatureAOV' + knobCounter + ', 1000, 40000 ) / 100 <= 66 ? clamp( ( ( ( log( clamp( parent.TemperatureAOV' + knobCounter + ', 1000, 40000 ) / 100 ) ) * 99.4708025861 ) - 161.1195681661 ), 0, 255 ) / 255  :   clamp( ( ( ( ( clamp( parent.TemperatureAOV' + knobCounter + ', 1000, 40000 ) / 100 ) - 60 ) ** -0.0755148492 )  * 288.1221695283 ), 0, 255 ) / 255',
        channel=1)
    tGrade['multiply'].setExpression(
        'clamp( parent.TemperatureAOV' + knobCounter + ', 1000, 40000 ) / 100 >= 66 ? 1 : clamp( parent.TemperatureAOV' + knobCounter + ', 1000, 40000 ) / 100 <= 19 ? 0 : clamp( ( ( log( ( ( clamp( parent.TemperatureAOV' + knobCounter + ', 1000, 40000 ) / 100 ) - 10 ) )  * 138.5177312231 ) - 305.0447927307 ), 0, 255 ) / 255',
        channel=2)

    thisGroup.end()

    knobs = thisGroup.knobs() 
    countOrig = []
    for knob in knobs:
        if knob[0:7] == "lightID":
            id = int(knob[7:])
            countOrig.append(id)

    countOrig.sort()

    thisGroup['lightCount'].setValue('<b>' + str(len(countOrig)) + '</b>')
    counter = ','.join(str(i) for i in countOrig)
    thisGroup['lights'].setValue(len(countOrig))


def Populate_Layers_Button():
    """
    Function for creating multiple light layers at once based on a list of AOVs from the connected render.

    """

    thisGroup = nuke.thisNode()

    if len(thisGroup.dependencies()) == 0:
        nuke.message('<font color=orange><h3><center>Connect a node with AOVs first')
    else:
        channels = nuke.layers(thisGroup)
        if not channels:

            nuke.message('<font color=orange><h3><center>No channels found')
        else:

            originalInfoText = thisGroup['info'].value()

            for n in nuke.allNodes():
                if "Static" not in n['label'].getValue():
                    nuke.delete(n)

            lastKnobName = 'last'

            allKnobs = list(thisGroup.knobs().keys())

            if lastKnobName in allKnobs:
                lastKnobIndex = allKnobs.index(lastKnobName)
                knobsToDelete = allKnobs[lastKnobIndex + 1:]

                for knobName in knobsToDelete:
                    thisGroup.removeKnob(thisGroup[knobName])

            task = nuke.ProgressTask('Building layer setup')
            layersList = []
            lightCheck = thisGroup['FilterAOV'].value()
            layersList = [x for x in channels if lightCheck in x]
            channelLayers = list(set(layersList))
            channelLayers.sort()
            channelLayersSliced = channelLayers[1:]
            channelLayersFirst = channelLayers[0:1]
            channelNum = (len(channelLayers))

            if channelNum < 2:
                if channelNum == 0:
                    nuke.message('<font color="orange"><h3><center>No light AOVs containing <font color="green">' + str(lightCheck) + '<font color="orange"> found</font></center></h3>')


                else:
                    nuke.message('<font color=orange><h3><center>Only found:\n<i>' + str(
                        channelLayers[0]) + '</i>\nNeed more layers to work!')

                knobInfoText = nuke.Text_Knob('info', '')
                thisGroup.addKnob(knobInfoText)
                knobInfoText.setValue(originalInfoText)
                knobInfoText.setFlag(nuke.STARTLINE)
                del (task)

            else:
                try:

                    thisGroup['LightAOV1'].setValue(channelLayers[0])
                    thisGroup['CopyAOV1'].setValue(1)

                    for index, currentAOV in enumerate(channelLayersSliced):
                        task.setMessage('Building layer for ' + currentAOV)
                        task.setProgress(int(((int(index) + 1) / channelNum) * 100))

                        allKnobs = thisGroup.knobs()
                        lightIDKnobs = [knob for knob in allKnobs if knob.startswith("lightID")]
                        uniqueNumbers = [int(knob.replace("lightID", "")) for knob in lightIDKnobs]
                        knobCounter = str(max(uniqueNumbers) + 1)

                        Light_Layer_Creation(thisGroup = thisGroup, knobCounter = knobCounter)

                        thisGroup.begin()
                        thisGroup['LightAOV' + knobCounter].setValue(currentAOV)

                        thisGroup.end()



                except StopIteration:
                    pass
                finally:
                    knobInfoText = nuke.Text_Knob('info', '')
                    thisGroup.addKnob(knobInfoText)
                    knobInfoText.setValue(originalInfoText)
                    knobInfoText.setFlag(nuke.STARTLINE)
                    del (task)


def Houdini_Copy_All_Layers_Button():
    """
    Wrap all the edits made on all layers into a dictionary + the current date and the name of the nuke script. Finally, store that in the clipboard so it can be used to import in Houdini.

    """
    from PySide2.QtGui import QGuiApplication
    import re

    n = nuke.thisNode()
    k = nuke.thisKnob()
    allKnobs = n.knobs()
    AOVPrefix = n['AOVPattern'].value()

    lightIDNumbers = []
    pattern = re.compile(r'lightID(\d+)$')
    for knob in n.knobs().values():
        match = pattern.search(knob.name())
        if match:
            lightIDNumbers.append(match.group(1))


    lightAOVKnobsList = [knob for knob in allKnobs if knob.startswith("LightAOV")]
    lightAOVNameList = [n[knobName].value() for knobName in lightAOVKnobsList]
    lightAOVNameListSliced = [entry[len(AOVPrefix):] if AOVPrefix.lower() in entry.lower() else entry for entry in lightAOVNameList]

    #Define HSV/RGB knob label text
    RGB = '<big><font style="background-color:#806060;">R<font style="background-color:#608071;">G<font style="background-color:#606680;">B'
    HSV = '<big><font style="background-color:#807460;">H<font style="background-color:#606680;">S<font style="background-color:#80607d;">V'

    #adding date and script name to dictionary
    scriptName = nuke.scriptName().split('/')
    dict = {'comment_info': f'Date of import: {date.today()} \nImport from: {scriptName[-1]}', }

    for index, lightAOV in enumerate(lightAOVNameListSliced):

        
        IntensityValue = n['IntensityAOV' + lightIDNumbers[index]].value()
        ExposureValue = n['ExposureAOV' + lightIDNumbers[index]].value()

        if n['HSV_RGBAOV' + lightIDNumbers[index]].label() == HSV:

            for node in n.nodes():
                if "Colour AdjustmentsAOV" + lightIDNumbers[index] in node['label'].getValue():
                    RGBValues = node['multiply'].value()

        if n['HSV_RGBAOV' + lightIDNumbers[index]].label() == RGB:
            RGBValues = n['RGBColourAOV' + lightIDNumbers[index]].value()

        # Get RGB Temperature value and multiply it with rgb values to be included when copying to houdini
        if n['DisableTemperatureAOV' + lightIDNumbers[index]].value() == 0:
            for node in n.nodes():
                if "TemperatureAOV" + lightIDNumbers[index] in node['label'].getValue():
                    TemperatureValue = node['multiply'].value()
                    TemperatureValue = TemperatureValue[:-1]

                    RGBValues = [x * y for x, y in zip(RGBValues, TemperatureValue)]

        RedValue = RGBValues[0]
        GreenValue = RGBValues[1]
        BlueValue = RGBValues[2]
        dict[lightAOV] = [
            IntensityValue,
            ExposureValue,
            RedValue,
            GreenValue,
            BlueValue,
        ]
        index = str(index + 1)

    clipboardText = f"""{dict}"""

    #Qt way to store something in the clipboard
    QGuiApplication.clipboard().setText(clipboardText)
    if not lightAOVNameListSliced:
        nuke.message("""<font color=orange><h3><center>Copy unsuccessful!
No lights to copy found""")

    else:
        nuke.message(f'<font color=green><h3><center>{", ".join(lightAOVNameListSliced)} '"""
Copy Successful, proceed pasting in Houdini
<font color=orange>Important! 
Overall Saturation information not copied across.""")

def Reset_All_Button():
    """
    Reset whole node to default.

    """

    thisGroup = nuke.thisNode()

    # Disconnect mask inputs
    for i in range(thisGroup.inputs()):
        thisGroup.setInput(i+1, None)

    # Delete internal nodes
    for n in nuke.allNodes():
        if "Static" not in n['label'].getValue():
            nuke.delete(n)



    originalInfoText = thisGroup['info'].value()
    if thisGroup['lights'].value() > 1:
        lastKnobName = 'last'
    else:
        lastKnobName = 'info'

    allKnobs = list(thisGroup.knobs().keys())
    if lastKnobName in allKnobs:
        lastKnobIndex = allKnobs.index(lastKnobName)
        knobsToDelete = allKnobs[lastKnobIndex + 1:]

        for knobName in knobsToDelete:
            thisGroup.removeKnob(thisGroup[knobName])

    if thisGroup['lights'].value() > 1:
        knobInfoText = nuke.Text_Knob('info', '')
        thisGroup.addKnob(knobInfoText)
        knobInfoText.setValue(originalInfoText)
        knobInfoText.setFlag(nuke.STARTLINE)

    n = nuke.thisNode()
    knobs = thisGroup.knobs()

    pointsOrig = []
    for knob in knobs:
        if knob[0:7] == "lightID":
            id = int(knob[7:])
            pointsOrig.append(id)

    pointsOrig.sort()

    thisGroup['lightCount'].setValue('<b>' + str(len(pointsOrig)) + '</b>')
    points = ','.join(str(i) for i in pointsOrig)
    thisGroup['lights'].setValue(len(pointsOrig))

    # Set default values for knobs
    thisGroup['IntensityAOV1'].setValue(1)
    thisGroup['ExposureAOV1'].setValue(0)
    thisGroup['OverallSatAOV1'].setValue(1)
    thisGroup['RGBColourAOV1'].setValue([1, 1, 1])
    thisGroup['HueAOV1'].setValue(0)
    thisGroup['SaturationAOV1'].setValue(0)
    thisGroup['ValueAOV1'].setValue(1)
    thisGroup['TemperatureAOV1'].setValue(6600)
    thisGroup['DisableTemperatureAOV1'].setValue(0)
    thisGroup['LightAOV1'].setValue('none')
    thisGroup['CopyAOV1'].setValue(1)
    thisGroup['SubtractAOV1'].setValue(0)
    thisGroup['SoloAOV1'].setValue(0)
    thisGroup['enableMaskAOV1'].setValue(0)

    thisGroup.begin()

    output = nuke.toNode('Output1')
    upstreamNode = output.input(0)
    startNodeName = upstreamNode.name()
    startNode = nuke.toNode(str(startNodeName))
    output['xpos'].setValue(int(startNode['xpos'].value()))
    output['ypos'].setValue(int(startNode['ypos'].value()) + 300)

    thisGroup.end()


def Collapse_layers_Button():
    n = nuke.thisNode()
    knobs = n.allKnobs()

    for knob in knobs:
        if knob.name().startswith("lightID"):
            knob.setValue(False)
