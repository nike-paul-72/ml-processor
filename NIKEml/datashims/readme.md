Note on Datashims solution.

1. Data shims are used to provide a unique code set in a common format that can query a data source and emit data in the target format (generally, parquet)
2. The data loader looks through the datashims folder, and then interatively loads and run each to acquire data.
3. All shims use an abstract base class (apiShimBaseClass.py) and must import and implement the methods in that ABC using a class declaration class dataShim(apiShim): and specifically implementing loadData method and dataSet property. 
4. Each datashim can implement their own methods, calls, etc, as needed to get the data required so long as they implement the required methods
5. All data shims must return a single data set (at this time) as a panda data frame.
6. The data loader will then persist the output to one or more formats (parquest, csv, json)
