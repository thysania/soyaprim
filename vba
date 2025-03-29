Sub AddRowToTable()
    Dim ws As Worksheet
    Dim tbl As ListObject
    
    ' Set the active sheet and find the first table
    Set ws = ActiveSheet
    Set tbl = ws.ListObjects(1) ' Assumes there's at least one table on the sheet
    
    ' Add a new row to the table
    tbl.ListRows.Add
End Sub

##########

Sub DeleteTableRow()
    Dim tbl As ListObject
    Dim rng As Range
    
    ' Check if the active cell is within a table
    On Error Resume Next
    Set tbl = ActiveCell.ListObject
    On Error GoTo 0
    
    If Not tbl Is Nothing Then
        ' Delete the row where the active cell is located
        tbl.ListRows(ActiveCell.Row - tbl.Range.Row + 1).Delete
    Else
        MsgBox "Active cell is not within a table.", vbExclamation
    End If
End Sub

##########

Sub GoToDEDUCT()
    On Error Resume Next
    Worksheets("DEDUCT").Activate
    If Err.Number <> 0 Then
        MsgBox "Sheet 'DEDUCT' does not exist.", vbExclamation
    End If
    On Error GoTo 0
End Sub

###########

Sub DuplicateTableRow()
    Dim tbl As ListObject
    Dim rowIndex As Long

    ' Check if the active cell is in a table
    On Error Resume Next
    Set tbl = ActiveCell.ListObject
    On Error GoTo 0

    If Not tbl Is Nothing Then
        ' Get the row index within the table
        rowIndex = ActiveCell.Row - tbl.Range.Row + 1
        
        ' Insert a new row directly below the current row
        tbl.ListRows.Add rowIndex + 1
        
        ' Copy the values from the current row to the new row
        tbl.ListRows(rowIndex + 1).Range.Value = tbl.ListRows(rowIndex).Range.Value
        
        MsgBox "Row duplicated successfully.", vbInformation
    Else
        MsgBox "Active cell is not within a table.", vbExclamation
    End If
End Sub

###########

Sub MoveTableRowUp()
    Dim tbl As ListObject
    Dim rowIndex As Long

    ' Check if the active cell is in a table
    On Error Resume Next
    Set tbl = ActiveCell.ListObject
    On Error GoTo 0

    If Not tbl Is Nothing Then
        rowIndex = ActiveCell.Row - tbl.Range.Row + 1
        If rowIndex > 1 Then
            ' Swap the current row with the row above
            tbl.ListRows(rowIndex).Range.Value = tbl.ListRows(rowIndex - 1).Range.Value
            tbl.ListRows(rowIndex - 1).Range.Value = ActiveCell.EntireRow.Value
            tbl.ListRows(rowIndex).Range.Delete xlShiftUp
            MsgBox "Row moved up successfully.", vbInformation
        Else
            MsgBox "Cannot move the first row up.", vbExclamation
        End If
    Else
        MsgBox "Active cell is not within a table.", vbExclamation
    End If
End Sub

############

Sub MoveTableRowDown()
    Dim tbl As ListObject
    Dim rowIndex As Long

    ' Check if the active cell is in a table
    On Error Resume Next
    Set tbl = ActiveCell.ListObject
    On Error GoTo 0

    If Not tbl Is Nothing Then
        rowIndex = ActiveCell.Row - tbl.Range.Row + 1
        If rowIndex < tbl.ListRows.Count Then
            ' Swap the current row with the row below
            tbl.ListRows(rowIndex).Range.Value = tbl.ListRows(rowIndex + 1).Range.Value
            tbl.ListRows(rowIndex + 1).Range.Value = ActiveCell.EntireRow.Value
            tbl.ListRows(rowIndex).Range.Delete xlShiftDown
            MsgBox "Row moved down successfully.", vbInformation
        Else
            MsgBox "Cannot move the last row down.", vbExclamation
        End If
    Else
        MsgBox "Active cell is not within a table.", vbExclamation
    End If
End Sub

###########

Sub UpdatePivotTableSource()
    Dim ws As Worksheet
    Dim pt As PivotTable
    Dim tbl As ListObject
    Dim newDataSource As String
    
    ' Set the active sheet
    Set ws = ActiveSheet
    
    ' Check if there are any tables in the active sheet
    If ws.ListObjects.Count = 0 Then
        MsgBox "No tables found in the active sheet.", vbExclamation
        Exit Sub
    End If
    
    ' Assume the first table in the active sheet is the intended data source
    Set tbl = ws.ListObjects(1)
    newDataSource = ws.Name & "!" & tbl.Name
    
    ' Update each pivot table's data source in the active sheet
    For Each pt In ws.PivotTables
        pt.ChangePivotCache ThisWorkbook.PivotCaches.Create( _
            SourceType:=xlDatabase, _
            SourceData:=newDataSource)
        pt.RefreshTable
    Next pt
    
    MsgBox "Pivot table data source updated successfully.", vbInformation
End Sub

#########

Sub PreparePrintArea()
    Dim ws As Worksheet
    Dim tbl As ListObject
    Dim pt As PivotTable
    Dim tblLastRow As Long
    Dim ptFirstRow As Long
    Dim printArea As String
    Dim pageBreakRow As Long

    ' Set the active sheet
    Set ws = ActiveSheet

    ' Ensure there is a table and pivot table on the sheet
    If ws.ListObjects.Count = 0 Then
        MsgBox "No table found on the active sheet.", vbExclamation
        Exit Sub
    End If
    
    If ws.PivotTables.Count = 0 Then
        MsgBox "No pivot table found on the active sheet.", vbExclamation
        Exit Sub
    End If

    ' Get the table and pivot table
    Set tbl = ws.ListObjects(1)
    Set pt = ws.PivotTables(1)

    ' Calculate the last row of the table and the first row of the pivot table
    tblLastRow = tbl.Range.Rows(tbl.Range.Rows.Count).Row
    ptFirstRow = pt.TableRange1.Row

    ' Set the print area from column A to L, including the pivot table
    printArea = "A1:L" & pt.TableRange1.Rows(pt.TableRange1.Rows.Count).Row
    ws.PageSetup.PrintArea = printArea

    ' Ensure table headers repeat on each page
    ws.PageSetup.PrintTitleRows = tbl.HeaderRowRange.Address

    ' Check if the pivot table starts near the page break
    On Error Resume Next
    pageBreakRow = ws.HPageBreaks(1).Location.Row
    On Error GoTo 0

    If pageBreakRow > 0 And pageBreakRow <= ptFirstRow Then
        ' Add a page break before the pivot table
        ws.HPageBreaks.Add Before:=ws.Rows(ptFirstRow)
    Else
        ' Remove any unnecessary page breaks before the pivot table
        Dim hpBreak As HPageBreak
        For Each hpBreak In ws.HPageBreaks
            If hpBreak.Location.Row = ptFirstRow Then
                ws.HPageBreaks.Remove hpBreak
                Exit For
            End If
        Next hpBreak
    End If

    MsgBox "Print area and page breaks prepared successfully.", vbInformation
End Sub