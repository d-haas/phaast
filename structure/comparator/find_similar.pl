###################################
# verify similar structure
sub info_duplicate_structures {
	my ($number_cycle,$numb_atoms,$coords_xyz,$file_energy,$name_file,$ncpus,$threshold_duplicate) = @_;
	my @array_coords = @{$coords_xyz};
	my @array_energy = @{$file_energy};
	my @array_name   = @{$name_file};
	#
	my $add = $number_cycle;
	#
	my %Info_Coords = ();
	#
	my %Info_Axis   = ();
	my %Info_Energy = ();
	my %Info_Name   = ();
	#
	my @array_keys  = ();
	for (my $i=0; $i < $add ; $i++) { 
		my $id            = sprintf("%.5d",$i);
		#
		$Info_Energy{$id} = $array_energy[$i];
		$Info_Name{$id}   = $array_name[$i];
		$Info_Axis{$id}   = $array_coords[$i];
		#
		my @abc           = split (/\n/,$array_coords[$i]);
		$Info_Coords{$id} = \@abc;
		push(@array_keys,$id);
	}
	my $pm        = new Parallel::ForkManager($ncpus);
	my $iteration = 0;
	#
	my $file_tmp = "Dupli.tmp";
	open (FILE, ">$file_tmp") or die "Unable to open XYZ file: $file_tmp";
	for ( my $x = 0 ; $x < scalar (@array_keys); $x = $x + 1 ) {
		$pm->start($iteration) and next;
		# All children process havee their own random.			
		srand();
		for ( my $y = 0 ; $y < scalar (@array_keys); $y = $y + 1 ) {
			if ( $x < $y ){
				#
				my @matrix_1 = @{$Info_Coords{$array_keys[$x]}};
				my @matrix_2 = @{$Info_Coords{$array_keys[$y]}};
				# # # # # # # # # # # # # # # # #
				#
				my @array_name_atoms_1 = ();
				my @array_coord_x_1    = ();
				my @array_coord_y_1    = ();
				my @array_coord_z_1    = ();
				#
				my @array_name_atoms_2 = ();
				my @array_coord_x_2    = ();
				my @array_coord_y_2    = ();
				my @array_coord_z_2    = ();	
				#
				for ( my $i = 0 ; $i < $numb_atoms ; $i = $i + 1 ){
					my @array_tabs_1  = split (/\s+/,$matrix_1[$i]);
					#
					my $radii_val;
					my $other_element = 0;
					if ( exists $Atomic_number{$array_tabs_1[0]} ) {
						# exists
						$radii_val = $Atomic_number{$array_tabs_1[0]};
						$array_name_atoms_1[++$#array_name_atoms_1] = $radii_val;
					} else {
						# not exists
						$radii_val = $array_tabs_1[0] ;
						$array_name_atoms_1[++$#array_name_atoms_1] = $radii_val;
					}
					$array_coord_x_1[++$#array_coord_x_1]   = $array_tabs_1[1];
					$array_coord_y_1[++$#array_coord_y_1]   = $array_tabs_1[2];
					$array_coord_z_1[++$#array_coord_z_1]   = $array_tabs_1[3];
				}
				#
				for ( my $i = 0 ; $i < $numb_atoms ; $i = $i + 1 ){
					my @array_tabs_2 = split (/\s+/,$matrix_2[$i]);
					#
					my $radii_val;
					my $other_element = 0;
					if ( exists $Atomic_number{$array_tabs_2[0]} ) {
						# exists
						$radii_val = $Atomic_number{$array_tabs_2[0]};
						$array_name_atoms_2[++$#array_name_atoms_2] = $radii_val;
					} else {
						# not exists
						$radii_val = $array_tabs_2[0] ;
						$array_name_atoms_2[++$#array_name_atoms_2] = $radii_val;
					}
					$array_coord_x_2[++$#array_coord_x_2]   = $array_tabs_2[1];
					$array_coord_y_2[++$#array_coord_y_2]   = $array_tabs_2[2];
					$array_coord_z_2[++$#array_coord_z_2]   = $array_tabs_2[3];
				}
				my $Springborg = Grigoryan_Springborg ($numb_atoms,\@array_coord_x_1 ,\@array_coord_y_1 ,\@array_coord_z_1 
																,\@array_coord_x_2 ,\@array_coord_y_2 ,\@array_coord_z_2 );												  
				#
				if ( $Springborg < $threshold_duplicate ) {
					my $number      = sprintf '%.6f', $Springborg;
					print FILE "$array_keys[$y]\n";
					print FILE "Value = $number\n";
				}
				#
			}
			$iteration++;
		}
		$pm->finish;	
	}
	close (FILE);
	# Paralel
	$pm->wait_all_children;
	# # #
	my @data_tmp = read_file ($file_tmp);	
	my @duplicates_name = ();
	my @Value_simi      = ();
	foreach my $info (@data_tmp) {
		if ( ($info =~ m/Value/) ) {
			my @array_tabs = ();
			@array_tabs    = split ('\s+',$info);
			push (@Value_simi,$array_tabs[2]);
		} else {
			push (@duplicates_name,$info);
		}
	}
	my @array_similar_coords = ();
	my @array_similar_energy = ();
	my @array_similar_files  = ();
	# Delete similar structures
	my @index_files = index_elements (\@duplicates_name,\@array_keys);
	#
	# Delete similar structures	
	for my $k (@index_files) {
		push (@array_similar_coords,$Info_Axis{$array_keys[$k]});
		push (@array_similar_energy,$Info_Energy{$array_keys[$k]});
		push (@array_similar_files ,$Info_Name{$array_keys[$k]});
		delete $Info_Coords{$array_keys[$k]};
	}
	#
	unlink ($file_tmp);
	#
	my @keys_arr    = keys %Info_Coords;
	my @axis_all    = ();
	my @energy_all 	= ();
	my @name_all 	= ();
	for my $co (@keys_arr) {
		push (@axis_all  ,$Info_Axis{$co});
		push (@energy_all,$Info_Energy{$co});
		push (@name_all  ,$Info_Name{$co});		
	}
	#
	return (\@axis_all,\@energy_all,\@name_all,\@array_similar_coords,\@array_similar_energy,\@array_similar_files);
}


pod=
This function, `info_duplicate_structures`, is designed to compare molecular structures and identify duplicates based on their geometric similarity. Here's a breakdown of how it works:

### **Purpose**
The function compares pairs of molecular structures to determine if they are duplicates based on a similarity threshold. It uses the Grigoryan-Springborg algorithm to calculate the similarity between molecular geometries.

### **Input Parameters**
1. `$number_cycle`: Number of structures to compare.
2. `$numb_atoms`: Number of atoms in each molecule.
3. `$coords_xyz`: Array of XYZ coordinates for all structures.
4. `$file_energy`: Array of energies for all structures.
5. `$name_file`: Array of filenames for all structures.
6. `$ncpus`: Number of CPU cores for parallel processing.
7. `$threshold_duplicate`: Similarity threshold (structures below this are considered duplicates).

### **Steps in the Function**
1. **Data Organization**:

 - Stores coordinates, energies, and filenames in hashes (`%Info_Coords`, `%Info_Energy`, `%Info_Name`).

 - Assigns each structure a unique ID (`$id`).

2. **Parallel Comparison**:

 - Uses `Parallel::ForkManager` to compare structures in parallel (for efficiency).

 - For each pair of structures (`$x` and `$y` where `$x < $y`), it:
     - Extracts atomic coordinates and element types.
     - Computes the Grigoryan-Springborg similarity metric.

3. **Grigoryan-Springborg Similarity**:

 - This metric measures the geometric difference between two structures.

 - If the computed value is below `$threshold_duplicate`, the structures are considered duplicates.

4. **Output Handling**:

 - Writes duplicate pairs to a temporary file (`Dupli.tmp`).

 - After processing, reads the file to identify duplicates.

 - Separates unique and duplicate structures.

5. **Return Values**:

 - Returns:
     - `@axis_all`: Coordinates of unique structures.
     - `@energy_all`: Energies of unique structures.
     - `@name_all`: Filenames of unique structures.
     - `@array_similar_coords`: Coordinates of duplicates.
     - `@array_similar_energy`: Energies of duplicates.
     - `@array_similar_files`: Filenames of duplicates.

### **Key Features**
- **Parallel Processing**: Speeds up comparison by distributing work across multiple CPU cores.
- **Grigoryan-Springborg Metric**: A robust method for comparing molecular geometries.
- **Threshold-Based Filtering**: Allows control over how similar structures must be to be considered duplicates.

### **How It Compares Two Molecules**
1. **Extract Coordinates**:

 - For each molecule, it parses XYZ coordinates and atomic numbers (or element symbols).
2. **Compute Similarity**:

 - Uses the Grigoryan-Springborg algorithm to compute a similarity score.
3. **Check Threshold**:

 - If the score is below `$threshold_duplicate`, the molecules are considered duplicates.

### **Example Usage**

```perl

my ($unique_coords, $unique_energies, $unique_names, 
    $duplicate_coords, $duplicate_energies, $duplicate_names) = 
    info_duplicate_structures(
        $num_structures, $num_atoms, \@coords, \@energies, \@filenames, 
        $ncpus, $threshold

    );

```

### **Notes**

- The function assumes input in XYZ format.
- The Grigoryan-Springborg metric is sensitive to atomic ordering, so structures must be aligned or preprocessed if necessary.
- The threshold (`$threshold_duplicate`) should be chosen carefully based on the desired sensitivity.
=cut
