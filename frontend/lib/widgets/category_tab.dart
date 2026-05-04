import 'package:flutter/material.dart';
import '../models/models.dart';

class CategoryTab extends StatelessWidget {
  final List<Category> categories;
  final String? selectedCategory;
  final Function(String?) onCategorySelected;

  const CategoryTab({
    super.key,
    required this.categories,
    this.selectedCategory,
    required this.onCategorySelected,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 50,
      decoration: BoxDecoration(
        color: Theme.of(context).scaffoldBackgroundColor,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: ListView(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 12),
        children: [
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 8),
            child: FilterChip(
              label: const Text('全部'),
              selected: selectedCategory == null,
              onSelected: (_) => onCategorySelected(null),
              selectedColor: Theme.of(context).colorScheme.tertiary.withOpacity(0.2),
              checkmarkColor: Theme.of(context).colorScheme.tertiary,
              labelStyle: TextStyle(
                color: selectedCategory == null
                    ? Theme.of(context).colorScheme.tertiary
                    : Theme.of(context).textTheme.bodyMedium?.color,
                fontWeight: selectedCategory == null ? FontWeight.w600 : FontWeight.normal,
              ),
            ),
          ),
          ...categories.map((category) {
            final isSelected = selectedCategory == category.code;
            return Padding(
              padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 8),
              child: FilterChip(
                label: Text(category.name),
                selected: isSelected,
                onSelected: (_) => onCategorySelected(category.code),
                selectedColor: Theme.of(context).colorScheme.tertiary.withOpacity(0.2),
                checkmarkColor: Theme.of(context).colorScheme.tertiary,
                labelStyle: TextStyle(
                  color: isSelected
                      ? Theme.of(context).colorScheme.tertiary
                      : Theme.of(context).textTheme.bodyMedium?.color,
                  fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
                ),
              ),
            );
          }),
        ],
      ),
    );
  }
}
