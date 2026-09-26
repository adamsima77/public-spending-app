<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('notice_lots', function (Blueprint $table) {
            $table->id();
            $table->text('lot_reference');                      // DL-Context-Lot / BT-137-Lot
            $table->text('title')->nullable();                 // DL-Title-Lot / BT-21-Lot
            $table->text('description')->nullable();           // BT-24-Lot
            $table->decimal('value', 14, 2)->nullable();        // BT-27-Lot_value
            $table->char('currency', 3)->nullable();
            $table->string('main_cpv', 10)->nullable();         // BT-262-Lot
            $table->string('nuts_code', 10)->nullable();        // BT-5071-Lot / BT-5141-Lot
            $table->text('award_criterion')->nullable();      // BT-539-Lot
            $table->timestamp('submission_deadline')->nullable(); // BT-131(d)-Lot / BT-131(t)-Lot
            $table->text('document_url')->nullable();          // BT-15-Lot
            $table->text('detail_url')->nullable();            // BT-18-Lot
            $table->timestamps();
            $table->jsonb('extra_fields')->nullable();
            $table->index('main_cpv');
            $table->index('nuts_code');
            $table->string('place_of_performance')->nullable()->after('nuts_code');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('notice_lots');
    }
};