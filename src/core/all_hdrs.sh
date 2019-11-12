cat PhysiCell_cell.h |tail -n +68 >all_hdrs.txt
echo "\n--------------------------------------------" >>all_hdrs.txt
cat PhysiCell_phenotype.h |tail -n +68 >>all_hdrs.txt
echo "\n--------------------------------------------" >>all_hdrs.txt
cat PhysiCell_cell_container.h |tail -n +68 >>all_hdrs.txt
echo "\n--------------------------------------------" >>all_hdrs.txt
cat PhysiCell_custom.h |tail -n +68 >>all_hdrs.txt
echo "\n--------------------------------------------" >>all_hdrs.txt
cat PhysiCell_constants.h |tail -n +68 >>all_hdrs.txt
echo "\n--------------------------------------------" >>all_hdrs.txt
cat PhysiCell_standard_models.h |tail -n +68 >>all_hdrs.txt
echo "\n--------------------------------------------" >>all_hdrs.txt
cat PhysiCell_utilities.h |tail -n +68 >>all_hdrs.txt
echo "\n--------------------------------------------" >>all_hdrs.txt
#PhysiCell.h			PhysiCell_constants.h		PhysiCell_phenotype.h
#PhysiCell_cell.h		PhysiCell_custom.h		PhysiCell_standard_models.h
#PhysiCell_cell_container.h	PhysiCell_digital_cell_line.h	PhysiCell_utilities.h
