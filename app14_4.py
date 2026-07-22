=== GetActiveSheet ===
Тип: object
Методы: GetVisible, SetVisible, SetActive, GetActiveCell, GetSelection, GetCells, GetRows, GetCols, GetUsedRange, GetName, SetName, GetIndex, GetRange, GetRangeByNumber, FormatAsTable, SetColumnWidth, SetRowHeight, SetDisplayGridlines, SetDisplayHeadings, SetLeftMargin, GetLeftMargin, SetRightMargin, GetRightMargin, SetTopMargin, GetTopMargin, SetBottomMargin, GetBottomMargin, SetPageOrientation, GetPageOrientation, GetPrintHeadings, SetPrintHeadings, GetPrintGridlines, SetPrintGridlines, GetDefNames, GetDefName, AddDefName, GetComments, Delete, SetHyperlink, AddChart, AddShape, AddImage, AddWordArt, AddOleObject, ReplaceCurrentImage, GetAllDrawings, GetAllImages, GetAllShapes, GetAllCharts, GetAllOleObjects, Move
=== GetRange ===
editor.GetRange: object
✅ Есть SetValue
sheet.GetRange: object
✅ Есть SetValue
=== Установка A1 ===
Записано через sheet.GetRange















<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial; padding: 10px; background: #f5f5f5; }
        button { padding: 12px; margin: 5px; width: 100%; cursor: pointer; font-size: 14px; background: #4CAF50; color: white; border: none; border-radius: 5px; }
        button:hover { background: #45a049; }
        textarea { width: 100%; height: 300px; font-family: monospace; font-size: 11px; background: #1e1e1e; color: #0f0; padding: 10px; border-radius: 4px; }
    </style>
</head>
<body>
    <h3>🔍 Тест API editor</h3>
    
    <button onclick="testSheet()">1. GetActiveSheet</button>
    <button onclick="testRange()">2. GetRange</button>
    <button onclick="testSetValue()">3. Установить A1</button>
    <button onclick="clearLog()">🧹 Очистить</button>
    
    <textarea id="log"></textarea>

    <script>
        var el = document.getElementById('log');
        function log(msg) { el.value += msg + '\n'; el.scrollTop = el.scrollHeight; }
        function clearLog() { el.value = ''; }

        function getEditor() { return window.parent.Asc.editor; }

        function testSheet() {
            log('=== GetActiveSheet ===');
            try {
                var sheet = getEditor().GetActiveSheet();
                log('Тип: ' + typeof sheet);
                if (sheet) {
                    var funcs = [];
                    for (var k in sheet) {
                        if (typeof sheet[k] === 'function') funcs.push(k);
                    }
                    log('Методы: ' + funcs.join(', '));
                }
            } catch(e) { log('❌ ' + e.message); }
        }

        function testRange() {
            log('=== GetRange ===');
            try {
                var editor = getEditor();
                // Пробуем editor.GetRange
                if (editor.GetRange) {
                    var r1 = editor.GetRange('A1');
                    log('editor.GetRange: ' + typeof r1);
                    if (r1 && typeof r1.SetValue === 'function') log('✅ Есть SetValue');
                }
                // Пробуем sheet.GetRange
                var sheet = editor.GetActiveSheet();
                if (sheet && sheet.GetRange) {
                    var r2 = sheet.GetRange('A1');
                    log('sheet.GetRange: ' + typeof r2);
                    if (r2 && typeof r2.SetValue === 'function') log('✅ Есть SetValue');
                }
            } catch(e) { log('❌ ' + e.message); }
        }

        function testSetValue() {
            log('=== Установка A1 ===');
            try {
                var editor = getEditor();
                var sheet = editor.GetActiveSheet();
                if (sheet && sheet.GetRange) {
                    sheet.GetRange('A1').SetValue('✅ Работает! ' + new Date().toLocaleTimeString());
                    log('Записано через sheet.GetRange');
                } else if (editor.GetRange) {
                    editor.GetRange('A1').SetValue('✅ Работает! ' + new Date().toLocaleTimeString());
                    log('Записано через editor.GetRange');
                } else if (editor.asc_setData) {
                    editor.asc_setData('A1', '✅ Работает через asc_setData');
                    log('Вызван asc_setData');
                }
            } catch(e) { log('❌ ' + e.message); }
        }
    </script>
</body>
</html>







=== Тест api.wb ===
✅ api.wb существует
Тип wb: object
Конструктор: cr
wb.getActiveSheet: undefined
wb.getActiveWorksheet: undefined
wb.GetActiveSheet: undefined
wb.activeSheet: undefined
wb.ActiveSheet: undefined
=== Методы wb ===
  fReplaceCallback()
  _init()
  destroy()
  scrollToOleSize()
  _createWorksheetView()
  _onSelectionNameChanged()
  _onSelectionMathInfoChanged()
  _onSelectionRangeChanged()
  _onCleanSelectRange()
  _isEqualRange()
  _updateSelectionInfo()
  _onWSSelectionChanged()
  _onInputMessage()
  _onScrollReinitialize()
  _onInitRowsCount()
  _onInitColsCount()
  _onScrollY()
  _onScrollX()
  _onSetSelection()
  _onGetSelectionState()
  _onSetSelectionState()
  isInnerOfWorksheet()
  _onChangeVisibleArea()
  _onChangeSelection()
  _onChangeSelectionDone()
  _onChangeSelectionRightClick()
  _onSelectionActivePointChanged()
  _onPointerDownPlaceholder()
  _onUpdateWorksheet()
  _onUpdateCursor()
  _onResizeElement()
  _onResizeElementDone()
  _onChangeFillHandle()
  _onChangeFillHandleDone()
  fillHandleDone()
  canFillHandle()
  _onMoveRangeHandle()
  _onMoveRangeHandleDone()
  _onMoveResizeRangeHandle()
  getOleSize()
Показано функций: 40
=== Получение активного листа ===
=== Работа с ячейкой A1 ===
=== window.parent.Asc ===
Тип Asc: object
Asc.editor: object
Asc.spreadsheet: undefined
Asc.api: undefined

Методы Asc.editor:
  onKeyDown()
  onKeyPress()
  onKeyUp()
  Begin_CompositeInput()
  Replace_CompositeText()
  End_CompositeInput()
  Set_CursorPosInCompositeText()
  Get_CursorPosInCompositeText()
  Get_MaxCursorPosInCompositeText()
  AddTextWithPr()
  beginInlineDropTarget()
  endInlineDropTarget()
  isEnabledDropTarget()
  constructor()
  sendEvent()
  _getHistory()
  _init()
  _loadSdkImages()
  asc_CheckGuiControlColors()
  getLogicDocument()
  asc_SendControlColors()
  asc_getFunctionArgumentSeparator()
  asc_getCurrencySymbols()
  asc_getAdditionalCurrencySymbols()
  asc_getLocaleExample()
  asc_parseDate()
  asc_convertNumFormatLocal2NumFormat()
  asc_convertNumFormat2NumFormatLocal()
  asc_getFormatCells()
  asc_getLocaleCurrency()
  asc_getCurrentListType()
  asc_setLocale()
  asc_getLocale()
  asc_getDecimalSeparator()
  asc_getGroupSeparator()
  asc_getFrozenPaneBorderType()
  asc_setFrozenPaneBorderType()
  _openDocument()
  initGlobalObjects()
  asc_DownloadAs()
  _saveCheck()
  _haveOtherChanges()
  _prepareSave()
  _printDesktop()
  asc_ChangePrintArea()
  asc_CanAddPrintArea()
  asc_SetPrintScale()
  asc_Copy()
  asc_Paste()
  asc_SpecialPasteWithCheck()
  asc_SpecialPasteData()
  pasteHelperSetSpecialPasteProps()
  pasteHelperSpecialPasteStart()
  asc_TextImport()
  asc_TextFromFileOrUrl()
  _getTextFromUrl()
  _getFileFromUrl()
  asc_GetCalcSettings()
  asc_UpdateCalcSettings()
  _getTextFromFile()
  asc_ImportXmlStart()
  showErrorMessage()
  asc_InsertDataTable()
  asc_ImportXmlEnd()
  _convertFromXml()
  endInsertDocumentUrls()
  asc_TextToColumns()
  asc_ShowSpecialPasteButton()
  asc_UpdateSpecialPasteButton()
  asc_HideSpecialPasteButton()
  asc_Cut()
  asc_PasteData()
  asc_CheckCopy()
  asc_SelectionCut()
  asc_bIsEmptyClipboard()
  asc_Undo()
  asc_Redo()
  asc_Resize()
  asc_addAutoFilter()
  asc_changeAutoFilter()
  asc_applyAutoFilter()
  asc_applyAutoFilterByType()
  asc_reapplyAutoFilter()
  asc_sortColFilter()
  asc_getAddFormatTableOptions()
  asc_clearFilter()
  asc_clearFilterColumn()
  asc_changeSelectionFormatTable()
  asc_changeFormatTableInfo()
  asc_applyAutoCorrectOptions()
  asc_insertCellsInTable()
  asc_deleteCellsInTable()
  asc_changeDisplayNameTable()
  asc_changeTableRange()
  asc_convertTableToRange()
  asc_getTablePictures()
  asc_getSlicerPictures()
  asc_setViewMode()
  asc_setFilteringMode()
  asc_setAdvancedOptions()
  asc_setPageOptions()
  asc_savePagePrintOptions()
  getDrawingObjects()
  getDrawingDocument()
  asc_getPageOptions()
  asc_setPageOption()
  asc_changeDocSize()
  asc_changePageMargins()
  asc_changePageOrient()
  asc_SetPrintHeadings()
  asc_SetPrintGridlines()
  asc_changePrintTitles()
  asc_getPrintTitlesRange()
  _onNeedParams()
  _onEndOpen()
  _openOnClient()
  _downloadAs()
  asc_initPrintPreview()
  asc_updatePrintPreview()
  getIndexPageByIndexSheet()
  asc_drawPrintPreview()
  asc_closePrintPreview()
  processSavedFile()
  asc_isDocumentModified()
  isDocumentModified()
  asc_registerCallback()
  asc_unregisterCallback()
  asc_SetDocumentPlaceChangedEnabled()
  asc_SetFastCollaborative()
  asc_setThumbnailStylesSizes()
  sheetsChanged()
  asyncFontsDocumentStartLoaded()
  asyncFontsDocumentEndLoaded()
  asyncFontEndLoaded()
  _loadFonts()
  openDocument()
  asc_CloseFile()
  openDocumentFromZip()
  openDocumentFromZip2()
  syncCollaborativeChanges()
  _applyFirstLoadChanges()
  _goToComment()
  _goToBookmark()
  _coAuthoringInitEnd()
  _onSaveChanges()
  _onApplyChanges()
  _onUpdateAfterApplyChanges()
  _onCleanSelection()
  _onDrawSelection()
  _onDrawFrozenPaneLines()
  _onUpdateAllSheetsLock()
  _onUpdateAllLayoutsLock()
  _onUpdateAllHeaderFooterLock()
  _onUpdateAllPrintScaleLock()
  _onUpdateLayoutMenu()
  _onShowDrawingObjects()
  _onShowComments()
  _onUpdateSheetsLock()
  _onUpdateLayoutLock()
  _onUpdatePrintAreaLock()
  _onUpdateHeaderFooterLock()
  _onUpdatePrintScaleLock()
  _onUpdateFrozenPane()
  _sendWorkbookStyles()
  startCollaborationEditing()
  endCollaborationEditing()
  _openDocumentEndCallback()
  _asc_setWorksheetRange()
  asc_setWorksheetRange()
  _onSaveCallbackInner()
  _isLockedEditing()
  _isLockedSparkline()
  _isLockedAddWorksheets()
  _addWorksheets()
  _addWorksheetsWithoutLock()
  asc_getWorksheetsCount()
  asc_getWorksheetName()
  asc_getWorksheetTabColor()
  asc_setWorksheetTabColor()
  asc_getActiveWorksheetIndex()
  asc_getActiveWorksheetId()
  asc_getWorksheetId()
  asc_isWorksheetHidden()
  asc_getDefinedNames()
  asc_setDefinedNames()
  asc_editDefinedNames()
  asc_delDefinedNames()
  asc_checkDefinedName()
  asc_getDefaultDefinedName()
  asc_getDefaultTableStyle()
  _onUpdateDefinedNames()
  _onUnlockDefName()
  _onCheckDefNameLock()
  asc_isWorksheetLockedOrDeleted()
  asc_isWorkbookLocked()
  asc_isLayoutLocked()
  asc_isHeaderFooterLocked()
  asc_isPrintScaleLocked()
  asc_isPrintAreaLocked()
  asc_getHiddenWorksheets()
  asc_showWorksheet()
  asc_hideWorksheet()
  asc_renameWorksheet()
  asc_addWorksheet()
  asc_insertWorksheet()
  asc_deleteWorksheet()
  asc_moveWorksheet()
  asc_copyWorksheet()
  asc_StartMoveSheet()
  asc_EndMoveSheet()
  asc_cleanSelection()
  asc_getZoom()
  asc_setZoom()
  asc_enableKeyEvents()
  asc_R7SetEmptyFormulaInCurrentCell()
  asc_R7GetIsPeriodicAutosave()
  asc_R7GetPeriodicAutosaveMinutes()
  asc_R7SetIsPeriodicAutosave()
  asc_R7SetPeriodicAutosaveMinutes()
  asc_TracePrecedents()
  asc_TraceDependents()
  asc_RemoveTraceArrows()
  asc_IsFocus()
  asc_searchEnabled()
  asc_findText()
  asc_replaceText()
  asc_endFindText()
  sync_setSearchCurrent()
  sync_startTextAroundSearch()
  sync_endTextAroundSearch()
  sync_getTextAroundSearchPack()
  sync_removeTextAroundSearch()
  sync_SearchEndCallback()
  sync_closeOleEditor()
  sync_changedElements()
  asc_StartTextAroundSearch()
  asc_SelectSearchElement()
  asc_findCell()
  asc_closeCellEditor()
  asc_setR1C1Mode()
  getR1C1Mode()
  asc_SetAutoCorrectHyperlinks()
  asc_setIncludeNewRowColTable()
  asc_getColumnWidth()
  asc_setColumnWidth()
  asc_showColumns()
  asc_hideColumns()
  asc_autoFitColumnWidth()
  asc_getRowHeight()
  asc_setRowHeight()
  asc_autoFitRowHeight()
  asc_showRows()
  asc_hideRows()
  asc_group()
  _canGroupPivot()
  asc_canGroupPivot()
  _groupPivot()
  asc_groupPivot()
  _ungroupPivot()
  asc_ungroupPivot()
  asc_ungroup()
  asc_checkAddGroup()
  asc_clearOutline()
  asc_changeGroupDetails()
  asc_insertCells()
  asc_deleteCells()
  asc_mergeCells()
  asc_sortCells()
  asc_emptyCells()
  asc_selectAreasByTypeCells()
  asc_drawDepCells()
  asc_mergeCellsDataLost()
  asc_sortCellsRangeExpand()
  setShowFormulas()
  getShowFormulas()
  setShowRuler()
  getShowRuler()
  asc_getSheetViewSettings()
  asc_setDisplayGridlines()
  asc_setDisplayHeadings()
  asc_setShowZeros()
  asc_setDate1904()
  asc_getDate1904()
  asc_drawingObjectsExist()
  asc_getChartObject()
  asc_addChartDrawingObject()
  getScaleCoefficientsForOleTableImage()
  asc_addTableOleObjectInOleEditor()
  asc_getBinaryInfoOleObject()
  asc_toggleChangeVisibleAreaOleEditor()
  asc_toggleShowVisibleAreaOleEditor()
  asc_editChartDrawingObject()
  addTrendlineToChart()
  asc_addImageDrawingObject()
  asc_AddMath()
  asc_AddMath2()
  asc_ConvertMathView()
  asc_SetMathProps()
  asc_showImageFileDialog()
  _addImageUrl()
  asc_addSignatureLine()
  asc_getAllSignatures()
  getSignatureLineSp()
  asc_CallSignatureDblClickEvent()
  gotoSignatureInternal()
  asc_getCurrentDrawingMacrosName()
  asc_assignMacrosToCurrentDrawing()
  asc_setSelectedDrawingObjectLayer()
  asc_setSelectedDrawingObjectAlign()
  asc_DistributeSelectedDrawingObjectHor()
  asc_DistributeSelectedDrawingObjectVer()
  asc_getSelectedDrawingObjectsCount()
  asc_canEditCrop()
  asc_startEditCrop()
  asc_endEditCrop()
  asc_cropFit()
  asc_cropFill()
  asc_addTextArt()
  asc_checkDataRange()
  asc_getBinaryFileWriter()
  asc_getWordChartObject()
  asc_cleanWorksheet()
  asc_setData()
  asc_getData()
  asc_addComment()
  asc_changeComment()
  asc_selectComment()
  asc_showComment()
  asc_findComment()
  asc_removeComment()
  asc_RemoveAllComments()
  asc_GetCommentLogicPositionv()
  asc_ResolveAllComments()
  asc_showComments()
  asc_hideComments()
  asc_FC_getListAvailable()
  asc_FC_getSelection()
  asc_FC_removeSelected()
  asc_FC_onControlAdded()
  asc_FC_getSettings()
  asc_FC_setSettings()
  setStartPointHistory()
  setEndPointHistory()
  asc_startAddShape()
  asc_endAddShape()
  asc_FC_add()
  asc_doubleClickOnTableOleObject()
  asc_canEditGeometry()
  asc_editPointsGeometry()
  asc_addShapeOnSheet()
  asc_addOleObjectAction()
  asc_editOleObjectAction()
  asc_startEditCurrentOleObject()
  asc_isAddAutoshape()
  onInkDrawerChangeState()
  asc_canAddShapeHyperlink()
  asc_canGroupGraphicsObjects()
  asc_groupGraphicsObjects()
  asc_canUnGroupGraphicsObjects()
  asc_unGroupGraphicsObjects()
  asc_changeShapeType()
  asc_getGraphicObjectProps()
  asc_GetSelectedText()
  asc_setGraphicObjectProps()
  ImgApply()
  asc_getOriginalImageSize()
  asc_setInterfaceDrawImagePlaceTextArt()
  asc_changeImageFromFile()
  asc_changeShapeImageFromFile()
  asc_changeArtImageFromFile()
  getImageDataFromSelection()
  putImageToSelection()
  getPluginContextMenuInfo()
  asc_putPrLineSpacing()
  asc_putLineSpacingBeforeAfter()
  asc_setDrawImagePlaceParagraph()
  asc_replaceLoadImageCallback()
  asyncImageEndLoaded()
  asyncImagesDocumentEndLoaded()
  asyncImageEndLoadedBackground()
  cleanSpelling()
  SpellCheck_CallBack()
  _spellCheckDisconnect()
  _spellCheckRestart()
  asc_setDefaultLanguage()
  asc_nextWord()
  asc_replaceMisspelledWord()
  asc_replaceMisspelledWords()
  asc_ignoreMisspelledWord()
  asc_ignoreNumbers()
  asc_ignoreUppercase()
  asc_cancelSpellCheck()
  asc_freezePane()
  asc_setSparklineGroup()
  asc_addSparklineGroup()
  asc_setListType()
  asc_setListType2()
  asc_getCellInfo()
  asc_getActiveCellCoord()
  asc_getAnchorPosition()
  asc_getCellEditMode()
  asc_getHeaderFooterMode()
  asc_getActiveRangeStr()
  asc_getIsTrackShape()
  asc_setCellFontName()
  asc_setCellFontSize()
  asc_setCellBold()
  asc_setCellItalic()
  asc_setCellUnderline()
  asc_setCellStrikeout()
  asc_setCellSubscript()
  asc_setCellSuperscript()
  asc_setCellAlign()
  asc_setCellVertAlign()
  asc_setCellTextWrap()
  asc_setCellTextShrink()
  asc_setCellTextColor()
  asc_setCellFill()
  asc_setCellBackgroundColor()
  asc_setCellBorders()
  asc_setCellFormat()
  asc_setCellAngle()
  asc_setCellStyle()
  asc_ChangeTextCase()
  asc_increaseCellDigitNumbers()
  asc_decreaseCellDigitNumbers()
  asc_increaseFontSize()
  asc_decreaseFontSize()
  asc_setCellIndent()
  asc_setCellProtection()
  asc_setCellLocked()
  asc_setCellHiddenFormulas()
  asc_checkProtectedRange()
  asc_checkLockedCells()
  asc_checkActiveCellPassword()
  asc_formatPainter()
  changeFormatPainterState()
  retrieveFormatPainterData()
  asc_showAutoComplete()
  asc_onMouseUp()
  asc_selectFunction()
  asc_insertHyperlink()
  asc_removeHyperlink()
  _doHlinkClickAction()
  asc_getFullHyperlinkLength()
  asc_cleanSelectRange()
  asc_insertInCell()
  asc_startWizard()
  asc_canEnterWizardRange()
  asc_insertArgumentsInFormula()
  asc_getFormulasInfo()
  asc_getFormulaLocaleName()
  asc_getFormulaNameByLocale()
  asc_calculate()
  asc_setFontRenderingMode()
  asc_setSelectionDialogMode()
  asc_SendThemeColors()
  getCurrentTheme()
  getGraphicController()
  asc_ChangeColorScheme()
  asc_ChangeColorSchemeByIdx()
  asc_AfterChangeColorScheme()
  asc_ApplyColorScheme()
  _autoSaveInner()
  _onUpdateDocumentCanSave()
  _onUpdateDocumentCanUndoRedo()
  _onCheckCommentRemoveLock()
  onUpdateDocumentModified()
  setLocalizationData()
  getLocalizationData()
  asc_setLocalization()
  asc_nativeOpenFile()
  asc_nativeCalculateFile()
  asc_nativeApplyChanges()
  asc_nativeApplyChanges2()
  _coAuthoringSetChanges()
  asc_nativeGetFile()
  asc_nativeGetFile3()
  asc_nativeGetFileData()
  asc_nativeCalculate()
  getPrintOptionsJson()
  asc_nativePrint()
  asc_nativePrintPagesCount()
  asc_nativeGetPDF()
  getCSVParamsFromPrintOptions()
  serializeActiveListToBase64()
  asc_nativeGetCSV()
  asc_canPaste()
  asc_endPaste()
  asc_Recalculate()
  pre_Paste()
  getDefaultFontFamily()
  getDefaultFontSize()
  _onEndLoadSdk()
  asc_OnShowContextMenu()
  _selectSearchingResults()
  asc_getAppProps()
  checkObjectsLock()
  asc_setCoreProps()
  getInternalCoreProps()
  asc_setGroupSummary()
  asc_getGroupSummaryRight()
  asc_getGroupSummaryBelow()
  asc_getSortProps()
  asc_setSortProps()
  asc_getRemoveDuplicates()
  asc_setRemoveDuplicates()
  asc_getCF()
  asc_getPreviewCF()
  asc_setCF()
  asc_clearCF()
  _onUpdateCFLock()
  _onUnlockCF()
  asc_getFullCFIcons()
  asc_getCFPresets()
  asc_getCFIconsByType()
  _onCheckCFRemoveLock()
  asc_isValidDataRefCf()
  asc_beforeInsertSlicer()
  asc_insertSlicer()
  asc_setSlicers()
  asc_Remove()
  asc_getDataValidationProps()
  asc_setDataValidation()
  asc_getProtectedRanges()
  asc_setProtectedRanges()
  _onUpdateProtectedRangesLock()
  _onUnlockProtectedRange()
  asc_checkProtectedRangesPassword()
  _onCheckProtectedRangeRemoveLock()
  asc_checkProtectedRangeName()
  asc_getProtectedSheet()
  asc_isProtectedSheet()
  asc_setProtectedSheet()
  asc_getProtectedWorkbook()
  asc_isProtectedWorkbook()
  asc_setProtectedWorkbook()
  asc_setSkin()
  turnOffSpecialModes()
  onUpdateRestrictions()
  isShowShapeAdjustments()
  isShowTableAdjustments()
  isShowEquationTrack()
  asc_getEscapeSheetName()
  asc_undoAllChanges()
  asc_restartCheckSpelling()
  asc_ConvertEquationToMath()
  showForeignSelectLabel()
  hideForeignSelectLabel()
  asc_addNamedSheetView()
  asc_getNamedSheetViews()
  asc_getActiveNamedSheetView()
  asc_deleteNamedSheetViews()
  _isLockedNamedSheetView()
  _onUpdateNamedSheetViewLock()
  _onUpdateAllSheetViewLock()
  isNamedSheetViewManagerLocked()
  asc_setActiveNamedSheetView()
  updateAllFilters()
  asc_EditSelectAll()
  asc_addCellWatches()
  asc_deleteCellWatches()
  asc_getCellWatches()
  setDrawGroupsRestriction()
  onWorksheetChange()
  asc_enterText()
  asc_correctEnterText()
  asc_getExternalReferences()
  asc_updateExternalReferences()
  asc_getRelativeLinkToFile()
  asc_removeExternalReferences()
  asc_fillHandleDone()
  asc_canFillHandle()
  getEyedropperImgData()
  asc_addUserProtectedRange()
  asc_changeUserProtectedRange()
  asc_deleteUserProtectedRange()
  asc_getUserProtectedRanges()
  _onUpdateUserProtectedRange()
  _onUnlockUserProtectedRanges()
  asc_checkUserProtectedRangeName()
  asc_SetSheetViewType()
  asc_GetSheetViewType()
  asc_StartGoalSeek()
  asc_CloseGoalClose()
  asc_PauseGoalSeek()
  asc_ContinueGoalSeek()
  asc_GoalSeekIteration()
  asc_isSharedWorkbook()
  changePageBreak()
  getPageBreaksDisableFlags()
  forEachSelectedObject()
  asc_GetFontThumbnailsPath()
  asc_setDocInfo()
  asc_changeDocInfo()
  asc_getEditorPermissions()
  asc_LoadDocument()
  asc_Save()
  forceSave()
  asc_setIsForceSaveOnUserSave()
  asc_getDocumentName()
  asc_getCoreProps()
  asc_isDocumentCanSave()
  asc_getCanUndo()
  asc_getCanRedo()
  can_CopyCut()
  asc_setAutoSaveGap()
  asc_decodeBuffer()
  SetDrawImagePreviewBulletForMenu()
  asc_getChartPreviews()
  asc_getTextArtPreviews()
  asc_getPropertyEditorShapes()
  asc_getPropertyEditorTextArts()
  asc_addImage()
  asc_onCloseChartFrame()
  asc_setInterfaceDrawImagePlaceShape()
  asc_spellCheckAddToDictionary()
  asc_spellCheckClearDictionary()
  asc_coAuthoringChatSendMessage()
  asc_coAuthoringGetUsers()
  asc_coAuthoringChatGetMessages()
  asc_coAuthoringDisconnect()
  asc_stopSaving()
  asc_continueSaving()
  asc_isOffline()
  asc_getUrlType()
  asc_prepareUrl()
  asc_getSessionToken()
  asc_nativeInitBuilder()
  asc_SetSilentMode()
  asc_pluginsRegister()
  asc_pluginRun()
  asc_pluginStop()
  asc_pluginResize()
  asc_pluginButtonClick()
  asc_pluginEnableMouseEvents()
  SetTextBoxInputMode()
  GetTextBoxInputMode()
  asc_InputClearKeyboardElement()
  asc_OnHideContextMenu()
  asc_getRequestSignatures()
  asc_AddSignatureLine2()
  asc_Sign()
  asc_RequestSign()
  asc_ViewCertificate()
  asc_SelectCertificate()
  asc_GetDefaultCertificate()
  asc_getSignatures()
  asc_isSignaturesSupport()
  asc_isProtectionSupport()
  asc_isAnonymousSupport()
  asc_RemoveSignature()
  asc_RemoveAllSignatures()
  asc_gotoSignature()
  asc_getSignatureSetup()
  asc_setCurrentPassword()
  asc_resetPassword()
  pluginMethod_AddComment()
  pluginMethod_ChangeComment()
  pluginMethod_RemoveComments()
  _changePivotSimple()
  updatePivotTables()
  _updatePivotTable()
  asc_getPivotInfo()
  asc_getPivotShowValueAsInfo()
  asc_getAddPivotTableOptions()
  asc_insertPivotNewWorksheet()
  asc_insertPivotExistingWorksheet()
  _asc_insertPivot()
  asc_refreshAllPivots()
  insertPivotChart()
  _isLockedPivot()
  _isLockedPivotAndConnectedBySlicer()
  _isLockedPivotAndConnectedByPivotCache()
  _changePivotWithLockUsingCommand()
  _changePivotWithLock()
  _changePivotWithLockExt()
  _changePivotAndConnectedBySlicerWithLock()
  _changePivotAndConnectedByPivotCacheWithLock()
  _changePivot()
  _changePivotRevert()
  _changePivotEndCheckError()
  asc_sortPivotByField()
  pivotShowDetails()
  GetDocument()
  CreateParagraph()
  CreateRange()
  CreateTable()
  CreateRun()
  CreateHyperlink()
  CreateImage()
  CreateShape()
  CreateChart()
  CreateOleObject()
  CreateRGBColor()
  CreateSchemeColor()
  CreatePresetColor()
  CreateSolidFill()
  CreateLinearGradientFill()
  CreateRadialGradientFill()
  CreatePatternFill()
  CreateBlipFill()
  CreateNoFill()
  CreateStroke()
  CreateGradientStop()
  CreateBullet()
  CreateNumbering()
  CreateInlineLvlSdt()
  CreateBlockLvlSdt()
  Save()
  LoadMailMergeData()
  GetMailMergeTemplateDocContent()
  GetMailMergeReceptionsCount()
  ReplaceDocumentContent()
  MailMerge()
  FromJSON()
  AddComment()
  attachEvent()
  detachEvent()
  ReplaceTextSmart()
  CoAuthoringChatSendMessage()
  ConvertDocument()
  CreateTextPr()
  CreateWordArt()
  GetFullName()
  GetDocumentId()
  GetDocuments()
  GetActiveDocument()
  private_CreateApiParagraph()
  private_CreateTextPr()
  private_CreateApiDocContent()
  private_CreateCheckBoxForm()
  private_CreateTextForm()
  private_CreateComboBoxForm()
  private_CreatePictureForm()
  private_CreateComplexForm()
  private_createWordArt()
  private_CreateApiRun()
  private_CreateApiHyperlink()
  private_CreateApiTextPr()
  private_CreateApiParaPr()
  private_CreateApiFill()
  private_CreateApiStroke()
  private_CreateApiGradStop()
  private_CreateApiUniColor()
  GetPresentation()
  CreateMaster()
  CreateLayout()
  CreatePlaceholder()
  CreateTheme()
  CreateThemeColorScheme()
  CreateThemeFormatScheme()
  CreateThemeFontScheme()
  CreateSlide()
  CreateGroup()
  private_checkDrawingUniNvPr()
  private_checkPlaceholders()
  private_CreateApiSlide()
  private_CreateApiMaster()
  private_CreateApiLayout()
  private_CreateApiPresentation()
  Format()
  AddSheet()
  GetSheets()
  SetLocale()
  GetLocale()
  GetActiveSheet()
  GetSheet()
  GetThemesColors()
  SetThemeColors()
  CreateNewHistoryPoint()
  CreateColorFromRGB()
  CreateColorByName()
  Intersect()
  GetSelection()
  AddDefName()
  GetDefName()
  GetRange()
  GetRangeByNumber()
  private_GetMailMergeFields()
  private_GetMailMergeMap()
  GetMailMergeData()
  RecalculateAllFormulas()
  GetComments()
  GetReferenceStyle()
  SetReferenceStyle()
  pluginMethod_OnEncryption()
  AddImageUrlAction()
  _saveLocalCheck()
  asc_DownloadAsNatural()
  _correctEmbeddedWork()
  sendReportError()
  _editorNameById()
  getEditorId()
  getDocumentFormat()
  getEditorErrorInfo()
  _loadModules()
  _onSuccessLoadModule()
  _onErrorLoadModule()
  _isLoadedModules()
  asc_loadFontsFromServer()
  isFrameEditor()
  getDocInfo()
  asc_isCrypto()
  isCopyOutEnabled()
  sync_CanCopyCutCallback()
  asc_LockTargetUpdate()
  asc_LockScrollToTarget()
  isPdfViewer()
  isLiveViewer()
  SendOpenProgress()
  sync_InitEditorFonts()
  sync_StartAction()
  sync_EndAction()
  sync_TryUndoInFastCollaborative()
  asc_setPermMode()
  asc_updatePermHighlights()
  asc_setHighlightPermMode()
  asc_changePermsEd()
  asc_addPerms()
  asc_removePerms()
  asc_R7HandlePeriodicAutosave()
  asc_setRestriction()
  getViewMode()
  getPermMode()
  getHighlightPermMode()
  asc_addRestriction()
  asc_removeRestriction()
  addTableOleObject()
  asc_addTableOleObject()
  asc_editTableOleObject()
  sendFromFrameToGeneralEditor()
  sendFromGeneralToFrameEditor()
  asc_getInformationBetweenFrameAndGeneralEditor()
  sendStartUploadImageActionToFrameEditor()
  addImageUrlsFromGeneralToFrameEditor()
  editTableOleObject()
  asc_SaveDrawingAsPicture()
  canEdit()
  isRestrictionForms()
  isRestrictionPerms()
  isRestrictionComments()
  isRestrictionSignatures()
  isRestrictionView()
  isLongActionBase()
  isLongAction()
  incrementCounterLongAction()
  decrementCounterLongAction()
  checkLongActionCallback()
  canUndoRedoByRestrictions()
  IsNeedDefaultFonts()
  onPrint()
  _openChartOrLocalDocument()
  _openEmptyDocument()
  _openVersionHistoryEndCallback()
  _onOpenCommand()
  openFileCryptCallback()
  asyncServerIdEndLoaded()
  asyncFontStartLoaded()
  asyncImageStartLoaded()
  asyncImagesDocumentStartLoaded()
  onDocumentContentReady()
  asc_createSmartArt()
  saveFromChanges()
  _onSaveCallback()
  _autoSave()
  _unlockDocument()
  checkChangesSize()
  _onEndPermissions()
  goTo()
  _coAuthoringInit()
  _coAuthoringCheckEndOpenDocument()
  _applyPreOpenLocks()
  asc_SpellCheckDisconnect()
  _coSpellCheckInit()
  _waitPrint()
  downloadAs()
  _downloadAsUsingServer()
  _downloadOriginalFile()
  processSavedFileAsTemplate()
  asc_generateSmartArtPreviews()
  asc_generateChartPreviews()
  asc_onOpenChartFrame()
  AddImageUrl()
  _uploadCallback()
  asc_loadLocalImageAndAction()
  asc_checkImageUrlAndAction()
  asc_addOleObject()
  asc_editOleObject()
  asc_selectSearchingResults()
  asc_setShapeNames()
  getShapeName()
  asc_canEditTableOleObject()
  asc_showRevision()
  asc_getAdvancedOptions()
  asc_Print()
  onEndLoadDocInfo()
  onEndLoadFile()
  sendStandartTextures()
  sendMathToMenu()
  sendMathTypesToMenu()
  asyncFontEndLoaded_MathDraw()
  getCurrentColorScheme()
  asc_GetCurrentColorSchemeName()
  asc_GetCurrentColorSchemeIndex()
  getColorSchemes()
  getColorSchemeByIdx()
  sendColorThemes()
  showVideoControl()
  hideVideoControl()
  _checkLicenseApiFunctions()
  isSliderDragged()
  asc_insertSymbol()
  asc_registerPlaceholderCallback()
  asc_uncheckPlaceholders()
  asc_nativeCheckPdfRenderer()
  Add_CompositeText()
  Remove_CompositeText()
  Input_UpdatePos()
  setInputParams()
  asc_isPermissionSupport()
  asc_getSignatureImage()
  getTargetOnBodyCoords()
  getAddedTextOnKeyDown()
  isIdle()
  checkInterfaceElementBlur()
  checkLastWork()
  setViewModeDisconnect()
  asc_GetPossibleNumberingLanguage()
  CheckDeprecatedBulletPreviewInfo()
  ParseBulletPreviewInformation()
  asc_setMacros()
  asc_getMacros()
  asc_setUserFunctionsRawData()
  asc_getUserFunctionsRawData()
  asc_getUserFunctions()
  _beforeEvalCommand()
  _afterEvalCommand()
  asc_R7SetServerTemplatesConfigs()
  asc_R7SetMacrosRunMode()
  asc_R7IsModeBlockedMacroses()
  asc_R7IsModeSafeMacroses()
  asc_R7SignMacros()
  asc_R7VerifyMacros()
  asc_runAutostartMacroses()
  asc_runMacros()
  asc_getAllMacrosNames()
  asc_getMacrosGuidByName()
  asc_getMacrosByGuid()
  asc_getUserPermissionToMakeRequestFromMacros()
  asc_setVisiblePasteButton()
  asc_getAutoCorrectMathSymbols()
  asc_getAutoCorrectMathFunctions()
  asc_resetToDefaultAutoCorrectMathSymbols()
  asc_resetToDefaultAutoCorrectMathFunctions()
  asc_deleteFromAutoCorrectMathSymbols()
  asc_deleteFromAutoCorrectMathFunctions()
  asc_AddOrEditFromAutoCorrectMathSymbols()
  asc_AddFromAutoCorrectMathFunctions()
  asc_refreshOnStartAutoCorrectMathSymbols()
  asc_refreshOnStartAutoCorrectMathFunctions()
  asc_updateFlagAutoCorrectMathSymbols()
  getMathInputType()
  asc_GetMathInputType()
  asc_SetMathInputType()
  getFileAsFromChanges()
  initShortcuts()
  initDefaultShortcuts()
  getShortcut()
  getCustomShortcutAction()
  asc_initShortcuts()
  asc_getShortcutAction()
  asc_removeShortcuts()
  asc_addCustomShortcutInsertSymbol()
  asc_addShortcut()
  asc_removeShortcutByCode()
  asc_removeShortcutByType()
  asc_getShortcutByEvent()
  asc_getShortcutByType()
  asc_getAllShortcuts()
  isLocalMode()
  isCloudModeCrypt()
  GetVersion()
  asc_isSupportFeature()
  asc_setDefaultBlitMode()
  sendInternalEvent()
  sendRemoteEvent()
  setHandlerOnClick()
  getHandlerOnClick()
  asc_onShowPopupWindow()
  onPluginContextMenuShow()
  onPluginContextMenuItemClick()
  onPluginCloseContextMenuItem()
  onPluginAddContextMenuItem()
  onPluginCheckContextMenuItems()
  onPluginUpdateContextMenuItem()
  asc_wopi_renameFile()
  setOpenedAt()
  signOform()
  getFormatPainter()
  getFormatPainterState()
  isFormatPainterOn()
  isFormatPainterOnMultiple()
  checkFormatPainterData()
  getFormatPainterData()
  clearFormatPainterData()
  sendPaintFormatEvent()
  clearEyedropperImgData()
  asc_startEyedropper()
  finishEyedropper()
  asc_finishEyedropper()
  cancelEyedropper()
  asc_cancelEyedropper()
  isEyedropperStarted()
  getEyedropperColor()
  checkEyedropperColor()
  asc_StartDrawInk()
  asc_StartInkEraser()
  asc_StopInkDrawer()
  stopInkDrawer()
  isInkDrawerOn()
  isDrawInkMode()
  isEraseInkMode()
  getInkPen()
  getInkCursorType()
  isCloudSaveAsLocalToDrawingFormat()
  localSaveToDrawingFormat()
  onLocalSaveToDrawingFormat()
  getSvgOptions()
  updateSvg()
  addImageLinkedByUrl()
  getRemoteDocuments()
  getAscFonts()
  getAscWord()
  getAscFormat()
  setOleDTO()
  getOleDTO()
  asc_SetDrawImagePreviewBulletForMenu()
  pluginMethod_GetVersion()
  pluginMethod_AddOleObject()
  pluginMethod_EditOleObject()
  pluginMethod_GetFontList()
  pluginMethod_InputText()
  pluginMethod_PasteHtml()
  pluginMethod_PasteText()
  pluginMethod_GetMacros()
  pluginMethod_GetUserFunctionsRawData()
  pluginMethod_IsModeBlockedMacroses()
  pluginMethod_IsModeSafeMacroses()
  pluginMethod_SignMacros()
  pluginMethod_VerifyMacros()
  pluginMethod_SetMacros()
  pluginMethod_SetUserFunctionsRawData()
  pluginMethod_ReloadFormulasList()
  pluginMethod_GetVBAMacros()
  pluginMethod_StartAction()
  pluginMethod_EndAction()
  pluginMethod_SetProperties()
  pluginMethod_ShowInputHelper()
  pluginMethod_UnShowInputHelper()
  pluginMethod_CoAuthoringChatSendMessage()
  pluginMethod_GetSelectionType()
  pluginMethod_ConvertDocument()
  pluginMethod_GetSelectedText()
  pluginMethod_ReplaceTextSmart()
  pluginMethod_GetFileToDownload()
  pluginMethod_GetImageDataFromSelection()
  pluginMethod_PutImageDataToSelection()
  checkInstalledPlugins()
  pluginMethod_GetInstalledPlugins()
  pluginMethod_RemovePlugin()
  pluginMethod_InstallPlugin()
  pluginMethod_UpdatePlugin()
  installDeveloperPlugin()
  pluginMethod_ShowButton()
  pluginMethod_GetKeychainStorageInfo()
  pluginMethod_SetKeychainStorageInfo()
  pluginMethod_OnSignWithKeychain()
  pluginMethod_OnDropEvent()
  pluginMethod_GetDocumentLang()
  pluginMethod_AddContextMenuItem()
  pluginMethod_UpdateContextMenuItem()
  pluginMethod_ShowWindow()
  pluginMethod_CloseWindow()
  pluginMethod_SendToWindow()
  pluginMethod_ResizeWindow()
  pluginMethod_MouseUpWindow()
  pluginMethod_MouseMoveWindow()
  onEndLoadFile2()
  local_sendEvent()
  asc_setLocalRestrictions()
  asc_getLocalRestrictions()
  asc_getLocalRestrictionsUser()





<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial; padding: 10px; background: #f5f5f5; }
        button { padding: 12px; margin: 5px; width: 100%; cursor: pointer; font-size: 14px; background: #4CAF50; color: white; border: none; border-radius: 5px; }
        button:hover { background: #45a049; }
        textarea { width: 100%; height: 350px; font-family: monospace; font-size: 11px; background: #1e1e1e; color: #0f0; padding: 10px; border-radius: 4px; }
    </style>
</head>
<body>
    <h3>🎯 Быстрый тест</h3>
    
    <button onclick="testWb()">1. Проверить api.wb</button>
    <button onclick="testWbMethods()">2. Только методы wb</button>
    <button onclick="testWbSheet()">3. wb.getActiveSheet()</button>
    <button onclick="testWbRange()">4. wb.GetRange("A1")</button>
    <button onclick="testAscAsc()">5. window.parent.Asc напрямую</button>
    <button onclick="clearLog()">🧹 Очистить</button>
    
    <textarea id="log"></textarea>

    <script>
        var el = document.getElementById('log');
        function log(msg) { el.value += msg + '\n'; el.scrollTop = el.scrollHeight; }
        function clearLog() { el.value = ''; }

        function getApi() { return window.parent.g_asc_plugins && window.parent.g_asc_plugins.api; }

        function testWb() {
            log('=== Тест api.wb ===');
            try {
                var api = getApi();
                if (!api) { log('❌ api недоступен'); return; }
                if (!api.wb) { log('❌ api.wb отсутствует'); return; }
                
                log('✅ api.wb существует');
                log('Тип wb: ' + typeof api.wb);
                log('Конструктор: ' + (api.wb.constructor ? api.wb.constructor.name : 'неизвестно'));
                
                // Проверяем только 3 ключевых свойства
                log('wb.getActiveSheet: ' + typeof api.wb.getActiveSheet);
                log('wb.getActiveWorksheet: ' + typeof api.wb.getActiveWorksheet);
                log('wb.GetActiveSheet: ' + typeof api.wb.GetActiveSheet);
                log('wb.activeSheet: ' + typeof api.wb.activeSheet);
                log('wb.ActiveSheet: ' + typeof api.wb.ActiveSheet);
                
            } catch(e) {
                log('❌ Ошибка: ' + e.message);
            }
        }

        function testWbMethods() {
            log('=== Методы wb ===');
            try {
                var api = getApi();
                if (!api || !api.wb) { log('❌ wb недоступен'); return; }
                
                var count = 0;
                for (var k in api.wb) {
                    if (typeof api.wb[k] === 'function' && count < 40) {
                        log('  ' + k + '()');
                        count++;
                    }
                }
                log('Показано функций: ' + count);
                
            } catch(e) {
                log('❌ Ошибка: ' + e.message);
            }
        }

        function testWbSheet() {
            log('=== Получение активного листа ===');
            try {
                var api = getApi();
                if (!api || !api.wb) return;
                
                var sheet = null;
                
                if (typeof api.wb.getActiveSheet === 'function') {
                    sheet = api.wb.getActiveSheet();
                    log('getActiveSheet(): ' + sheet);
                }
                if (typeof api.wb.getActiveWorksheet === 'function') {
                    sheet = api.wb.getActiveWorksheet();
                    log('getActiveWorksheet(): ' + sheet);
                }
                if (typeof api.wb.GetActiveSheet === 'function') {
                    sheet = api.wb.GetActiveSheet();
                    log('GetActiveSheet(): ' + sheet);
                }
                
                if (sheet && typeof sheet === 'object') {
                    log('✅ Лист получен! Его методы:');
                    for (var k in sheet) {
                        if (typeof sheet[k] === 'function') {
                            log('  ' + k + '()');
                        }
                    }
                }
                
            } catch(e) {
                log('❌ Ошибка: ' + e.message);
            }
        }

        function testWbRange() {
            log('=== Работа с ячейкой A1 ===');
            try {
                var api = getApi();
                if (!api || !api.wb) return;
                
                // Пробуем GetRange
                if (typeof api.wb.GetRange === 'function') {
                    var range = api.wb.GetRange('A1');
                    log('GetRange("A1"): ' + range);
                    if (range && typeof range.SetValue === 'function') {
                        range.SetValue('УРА!!! ЗАРАБОТАЛО!');
                        log('✅ Значение установлено!');
                    }
                }
                
                // Пробуем getRange
                if (typeof api.wb.getRange === 'function') {
                    var range2 = api.wb.getRange('A1');
                    log('getRange("A1"): ' + range2);
                }
                
            } catch(e) {
                log('❌ Ошибка: ' + e.message);
            }
        }

        function testAscAsc() {
            log('=== window.parent.Asc ===');
            try {
                var Asc = window.parent.Asc;
                if (!Asc) { log('❌ Asc недоступен'); return; }
                
                log('Тип Asc: ' + typeof Asc);
                
                // Ищем editor
                log('Asc.editor: ' + typeof Asc.editor);
                log('Asc.spreadsheet: ' + typeof Asc.spreadsheet);
                log('Asc.api: ' + typeof Asc.api);
                
                // Пробуем Asc.editor
                if (Asc.editor) {
                    log('\nМетоды Asc.editor:');
                    for (var k in Asc.editor) {
                        if (typeof Asc.editor[k] === 'function') {
                            log('  ' + k + '()');
                        }
                    }
                }
                
            } catch(e) {
                log('❌ Ошибка: ' + e.message);
            }
        }

        window.onload = function() {
            log('=== Плагин готов ===');
            log('Нажимайте кнопки 1-5 по порядку');
        };
    </script>
</body>
</html>
