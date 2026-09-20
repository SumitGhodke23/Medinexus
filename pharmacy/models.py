from django.db import models


class Medicine(models.Model):
	medicine_id = models.AutoField(primary_key=True)
	medicine_name = models.CharField(max_length=200)
	category = models.CharField(max_length=100, blank=True)
	quantity = models.PositiveIntegerField(default=0)
	reorder_level = models.PositiveIntegerField(default=10)
	unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	expiry_date = models.DateField(blank=True, null=True)
	supplier = models.CharField(max_length=200, blank=True)
	active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["medicine_name"]

	@property
	def needs_reorder(self):
		return self.quantity <= self.reorder_level

	def __str__(self):
		return self.medicine_name
